import pytest
from pathlib import Path
import shutil

import accml.core.bl.liasion_translator_setup as lts
from accml.core.bl.unit_conversion import EnergyDependentLinearUnitConversion
from accml.core.model.identifiers import ConversionID, LatticeElementPropertyID, DevicePropertyID


@pytest.fixture(scope="module")
def config_dir(tmp_path_factory):
    """Create a temporary copy of the real config data."""
    tmp_dir = tmp_path_factory.mktemp("config_data")

    base_config_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "accml"
        / "custom"
        / "epics"
        / "accml_lib"
        / "config_data"
    )

    shutil.copy(base_config_path / "magnets.yaml", tmp_dir / "magnets.yaml")
    shutil.copy(base_config_path / "power_converters.yaml", tmp_dir / "power_converters.yaml")

    return tmp_dir


def test_build_managers_with_real_data(config_dir):
    """End-to-end test of building YellowPages, LiaisonManager, and TranslatorService."""
    yp, lm, tm = lts.build_managers(config_dir)

    # --- YellowPages checks ---
    assert yp is not None
    assert hasattr(yp, "quadrupole_names")
    assert len(yp.quadrupole_names()) > 0

    # --- LiaisonManager checks ---
    assert lm is not None
    assert hasattr(lm, "forward_lut")
    assert hasattr(lm, "inverse_lut")
    assert all(isinstance(k, LatticeElementPropertyID) for k in lm.forward_lut)
    assert all(isinstance(v, DevicePropertyID) for v in lm.forward_lut.values())

    # --- TranslatorService checks (behavioral, not internal attr) ---
    assert tm is not None
    # find one known mapping and ensure it can retrieve conversion
    sample_magnet = yp.quadrupole_names()[0]
    conv_id = ConversionID(
        lattice_property_id=LatticeElementPropertyID(element_name=sample_magnet, property="main_strength"),
        device_property_id=DevicePropertyID(device_name=lm.forward_lut[
            LatticeElementPropertyID(element_name=sample_magnet, property="main_strength")
        ].device_name, property="set_current"),
    )

    # Call behaviorally
    conversion_obj = tm.get(conv_id)
    assert isinstance(conversion_obj, EnergyDependentLinearUnitConversion)
    assert hasattr(conversion_obj, "slope")
    assert hasattr(conversion_obj, "intercept")


def test_build_managers_detects_duplicate_names(monkeypatch, config_dir):
    """Ensure duplicate magnet names raise an AssertionError."""
    # Monkeypatch ConfigService.get_magnets to return duplicates
    cs = lts.ConfigService(
        magnet_path=config_dir / "magnets.yaml",
        pc_path=config_dir / "power_converters.yaml",
    )
    cs.load()
    magnets = cs.get_magnets()
    magnets.append(magnets[0])  # duplicate

    monkeypatch.setattr(cs, "get_magnets", lambda: magnets)
    monkeypatch.setattr(lts, "ConfigService", lambda *a, **k: cs)

    with pytest.raises(AssertionError):
        lts.build_managers(config_dir)


def test_load_managers_cache(monkeypatch):
    """Ensure @lru_cache prevents multiple builds."""
    count = {"n": 0}

    def fake_build(path):
        count["n"] += 1
        return ("yp", "lm", "tm")

    monkeypatch.setattr(lts, "build_managers", fake_build)

    result1 = lts.load_managers()
    result2 = lts.load_managers()
    assert result1 == result2
    assert count["n"] == 1

# test_data_integrity.py
import pytest
from accml_lib.core.model.utils.identifiers import (
    LatticeElementPropertyID,
    DevicePropertyID,
    ConversionID,
)
from accml_lib.core.bl.unit_conversion import EnergyDependentLinearUnitConversion
from accml_lib.custom.bessyii.liasion_translator_setup import load_managers


@pytest.fixture(scope="module")
def managers():
    """Load cached managers once."""
    yp, lm, tm = load_managers()
    return yp, lm, tm


def _is_main_pair(lep: LatticeElementPropertyID, dp: DevicePropertyID) -> bool:
    return lep.property == "main_strength" and dp.property == "set_current"


def test_forward_inverse_consistency(managers):
    """
    Each *main* forward mapping must exist in inverse mapping.
    (inverse_lut contains only main entries)
    """
    _, lm, _ = managers
    for lep, dp in lm.forward_lut.items():
        if not _is_main_pair(lep, dp):
            continue  # skip delta pairs; inverse_lut is main-only
        assert dp in lm.inverse_lut, f"Device {dp} missing in inverse LUT"
        assert lep in lm.inverse_lut[dp], f"{lep} not found under {dp} in inverse LUT"


@pytest.mark.skip
def test_inverse_key_count_matches_unique_devices(managers):
    """
    Number of inverse LUT keys == number of unique *main* DevicePropertyIDs in forward LUT.

    Todo:
        check if the numbers are as expected
    """
    _, lm, _ = managers
    main_dps = {
        dp for lep, dp in lm.forward_lut.items() if _is_main_pair(lep, dp)
    }
    assert len(lm.inverse_lut) == len(
        main_dps
    ), f"inverse_lut keys={len(lm.inverse_lut)} vs unique main devices={len(main_dps)}"


@pytest.mark.skip
def test_inverse_covers_all_main_leps(managers):
    """
    Total lattice elements listed in inverse LUT == number of *main* entries in forward LUT.

    Todo:
        check if the test of length of returned sequence is correct

    """
    _, lm, _ = managers
    forward_main_count = sum(1 for lep, dp in lm.forward_lut.items() if _is_main_pair(lep, dp))
    inverse_total = sum(len(leps) for leps in lm.inverse_lut.values())
    assert inverse_total == forward_main_count, (
        f"inverse covers {inverse_total} main leps, expected {forward_main_count}"
    )


def test_unique_lattice_ids_in_forward(managers):
    """
    Forward LUT keys (LEPs) must be unique by definition.
    Values (DPs) can repeat because multiple magnets share converters.
    """
    _, lm, _ = managers
    assert len(set(lm.forward_lut.keys())) == len(lm.forward_lut), "Duplicate LEPs in forward LUT"


def test_conversion_roundtrip(managers):
    """Conversions should be numerically reversible (sample)."""
    _, lm, tm = managers
    # sample the first 10 main pairs
    sample = [item for item in lm.forward_lut.items() if _is_main_pair(*item)][:10]
    for lep, dp in sample:
        cid = ConversionID(lattice_property_id=lep, device_property_id=dp)
        conv = tm.get(cid)
        assert isinstance(conv, EnergyDependentLinearUnitConversion), f"No conversion for {cid}"
        v_model = 1.0
        v_dev = conv.forward(v_model)
        v_back = conv.inverse(v_dev)
        assert abs(v_back - v_model) < 1e-6, f"Non-reversible conversion for {lep}"


def test_yellowpages_consistency(managers):
    """Every YellowPages quadrupole must appear in forward LUT (main)."""
    yp, lm, _ = managers
    for qname in yp.quadrupole_names():
        lep = LatticeElementPropertyID(element_name=qname, property="main_strength")
        assert lep in lm.forward_lut, f"{qname} missing in forward LUT (main_strength)"


def test_every_forward_pair_has_conversion(managers):
    """
    Every forward pair (main and delta) must have a Translator entry.
    (Translator LUT includes both.)
    """
    _, lm, tm = managers
    missing = []
    for lep, dp in lm.forward_lut.items():
        cid = ConversionID(lattice_property_id=lep, device_property_id=dp)
        if cid not in tm.lut:
            missing.append((lep, dp))
    assert not missing, f"Missing conversion for {len(missing)} pairs"

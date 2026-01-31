# tests/test_as_json_compatible.py
import pytest

from accml.custom.bluesky.utils import as_json_compatible_device_id
from accml_lib.core.model.utils.tango_resource_locator import TangoResourceLocator


# adjust this import to match your module name if different


def test_as_json_compatible_device_id_with_string_returns_same():
    s = "domain/fam/member"          # a normal TRL-like string
    assert as_json_compatible_device_id(s) is s or as_json_compatible_device_id(s) == s

    empty = ""
    assert as_json_compatible_device_id(empty) == ""

    # unicode / non-ascii should be preserved (function treats str as already compatible)
    u = "dømain/fäm/member-µ"
    assert as_json_compatible_device_id(u) == u


def test_as_json_compatible_with_trl_object_uses_json_compatible():
    # dots ensure clear_token replacement; expected json_compatible uses underscores
    trl = TangoResourceLocator(domain="a.b", family="c.d", member="e.f")
    expected = "a_b__c_d__e_f"
    assert trl.json_compatible() == expected
    assert as_json_compatible_device_id(trl) == expected


@pytest.mark.parametrize("bad_value, expected_type_name", [
    (42, "int"),
    (3.14, "float"),
    (None, "NoneType"),
    (object(), "object"),
])
def test_as_json_compatible_with_invalid_types_raises_typeerror(bad_value, expected_type_name):
    with pytest.raises(TypeError) as excinfo:
        as_json_compatible_device_id(bad_value)
    # message should mention the offending type name for easier debugging
    assert expected_type_name in str(excinfo.value)


def test_as_json_compatible_str_vs_trl_different_behaviour():
    # If caller passes a string that looks like json_compatible, function returns it unchanged.
    s = "a_b__c_d__e_f"
    assert as_json_compatible_device_id(s) == s

    # If caller passes a TangoResourceLocator, the produced json_compatible must equal str input above
    trl = TangoResourceLocator(domain="a.b", family="c.d", member="e.f")
    assert as_json_compatible_device_id(trl) == s

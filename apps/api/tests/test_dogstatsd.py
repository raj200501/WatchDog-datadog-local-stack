import pytest

from apps.api.app.utils.dogstatsd import parse_line, DogstatsdParseError


def test_parse_line_basic():
    parsed = parse_line("cpu.util:0.5|g|#service:web,env:prod")
    assert parsed["name"] == "cpu.util"
    assert parsed["value"] == 0.5
    assert parsed["tags"]["service"] == "web"
    assert parsed["service"] == "web"


def test_parse_line_invalid():
    with pytest.raises(DogstatsdParseError):
        parse_line("nope")

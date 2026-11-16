import datetime

import pytest

from rs import cli


def test_parse_minimal():
    a = cli.parse_args(["abc"])
    assert a.submission_id == "abc"
    assert a.as_of is None
    assert a.json is False


def test_parse_all_options():
    a = cli.parse_args(["abc", "--as-of", "2026-11-16", "--json"])
    assert a.as_of == datetime.date(2026, 11, 16)
    assert a.json is True


def test_bad_as_of_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as e:
        cli.parse_args(["abc", "--as-of", "notadate"])
    assert e.value.code != 0
    assert "as-of" in capsys.readouterr().err

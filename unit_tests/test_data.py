import json
import urllib.error

import pytest

from rs import cli, data


def fake_http(payload, calls=None):
    def get(url, headers):
        if calls is not None:
            calls.append((url, headers))
        return json.dumps(payload).encode()
    return get


def test_fetch_submission_returns_row_and_sends_key():
    calls = []
    row = {"id": "abc", "status": "REVIEW_PENDING"}
    got = data.fetch_submission("abc", http_get=fake_http([row], calls))
    assert got == row
    url, headers = calls[0]
    assert "/rest/v1/submissions" in url and "id=eq.abc" in url
    assert headers["apikey"] == data.API_KEY


def test_fetch_submission_unknown_returns_none():
    assert data.fetch_submission("nope", http_get=fake_http([])) is None


def test_fetch_submission_quotes_id():
    calls = []
    data.fetch_submission("a&b=c", http_get=fake_http([], calls))
    assert "a&b=c" not in calls[0][0]


def test_fetch_users_and_orgs_hit_their_tables():
    calls = []
    data.fetch_users(http_get=fake_http([], calls))
    data.fetch_orgs(http_get=fake_http([], calls))
    assert "/rest/v1/users" in calls[0][0]
    assert "/rest/v1/orgs" in calls[1][0]


def test_network_error_becomes_datasourceerror():
    def boom(url, headers):
        raise urllib.error.URLError("down")
    with pytest.raises(data.DataSourceError):
        data.fetch_submission("abc", http_get=boom)


def test_bad_json_becomes_datasourceerror():
    with pytest.raises(data.DataSourceError):
        data.fetch_submission("abc", http_get=lambda u, h: b"<html>")


def test_main_unknown_submission_exits_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(data, "fetch_submission", lambda sid, **k: None)
    assert cli.main(["abc"]) != 0
    assert "unknown submission" in capsys.readouterr().err


def test_main_data_error_exits_nonzero(monkeypatch, capsys):
    def boom(sid, **k):
        raise data.DataSourceError("db unreachable")
    monkeypatch.setattr(data, "fetch_submission", boom)
    assert cli.main(["abc"]) != 0
    assert "db unreachable" in capsys.readouterr().err

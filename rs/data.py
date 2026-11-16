import json
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://mpgyuiepgsevezlivlxp.supabase.co/rest/v1"
API_KEY = "sb_publishable_hBLhTOAw_B4-2Lf_Q4pQgw_TThlpjJe"


class DataSourceError(Exception):
    pass


def _default_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def _fetch(path, params, http_get):
    url = f"{BASE_URL}/{path}?{urllib.parse.urlencode(params)}"
    try:
        body = (http_get or _default_get)(url, {"apikey": API_KEY})
        return json.loads(body)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise DataSourceError(f"cannot reach database: {e}") from e
    except ValueError as e:
        raise DataSourceError(f"unexpected database response: {e}") from e


def fetch_submission(submission_id, http_get=None):
    rows = _fetch("submissions", {"select": "*", "id": f"eq.{submission_id}"}, http_get)
    return rows[0] if rows else None


def fetch_users(http_get=None):
    return _fetch("users", {"select": "*"}, http_get)


def fetch_orgs(http_get=None):
    return _fetch("orgs", {"select": "*"}, http_get)

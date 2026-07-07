from cyberclip.userAction.UrlQueryAction import QueryUrlQueryAction


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_extract_report_ids():
    action = QueryUrlQueryAction()

    fake_json = {
        "reports": [
            {"report_id": "abc123"},
            {"report_id": "xyz456"},
            {"report_id": "abc123"},
        ]
    }

    report_ids = action._extract_report_ids(fake_json)

    assert report_ids == ["abc123", "xyz456"]


def test_query_urlquery_runs_multiple_newline_queries(monkeypatch):
    calls = []

    def fake_get(url, headers=None, params=None, timeout=None):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        return FakeResponse(
            {
                "query": params["query"],
                "total_hits": 1,
                "reports": [{"report_id": f'{params["query"]}-report'}],
            }
        )

    monkeypatch.setattr("cyberclip.userAction.UrlQueryAction.requests.get", fake_get)

    action = QueryUrlQueryAction()
    action.conf = {"api_key": "token"}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "example.com\n8.8.8.8"},
        "Max results": {"type": "text", "value": "5"},
        "Report mode": {"type": "bool", "value": False},
    }

    result = action.execute()

    assert calls == [
        {
            "url": "https://api.urlquery.net/public/v1/search/reports/",
            "headers": {
                "accept": "application/json",
                "content-type": "application/json",
                "X-APIKEY": "token",
            },
            "params": {"query": "example.com", "limit": 5, "offset": 0},
            "timeout": 20,
        },
        {
            "url": "https://api.urlquery.net/public/v1/search/reports/",
            "headers": {
                "accept": "application/json",
                "content-type": "application/json",
                "X-APIKEY": "token",
            },
            "params": {"query": "8.8.8.8", "limit": 5, "offset": 0},
            "timeout": 20,
        },
    ]
    assert result["example.com"]["query"] == "example.com"
    assert result["8.8.8.8"]["reports"][0]["report_id"] == "8.8.8.8-report"


def test_query_urlquery_report_mode_fetches_full_reports(monkeypatch):
    calls = []

    def fake_get(url, headers=None, params=None, timeout=None):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        if url.endswith("/search/reports/"):
            return FakeResponse(
                {
                    "query": params["query"],
                    "reports": [
                        {"report_id": "r1"},
                        {"report_id": "r2"},
                    ],
                }
            )
        if url.endswith("/report/r1"):
            return FakeResponse({"report_id": "r1", "status": "done"})
        if url.endswith("/report/r2"):
            return FakeResponse({"report_id": "r2", "status": "done"})
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr("cyberclip.userAction.UrlQueryAction.requests.get", fake_get)

    action = QueryUrlQueryAction()
    action.conf = {"api_key": "token"}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "example.com"},
        "Max results": {"type": "text", "value": "2"},
        "Report mode": {"type": "bool", "value": True},
    }

    result = action.execute()

    assert [entry["reportId"] for entry in result] == ["r1", "r2"]
    assert result[0]["report"]["status"] == "done"
    assert calls[0]["params"] == {"query": "example.com", "limit": 2, "offset": 0}

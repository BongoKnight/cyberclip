from cyberclip.userAction.ShodanAction import QueryShodanAction


class FakeShodanClient:
    calls = []

    def __init__(self, api_key):
        self.api_key = api_key

    def search(
        self,
        query,
        page=1,
        limit=None,
        offset=None,
        facets=None,
        minify=True,
        fields=None,
    ):
        self.calls.append(
            {
                "method": "search",
                "api_key": self.api_key,
                "query": query,
                "page": page,
                "limit": limit,
                "offset": offset,
                "facets": facets,
                "minify": minify,
                "fields": fields,
            }
        )
        return {"total": 1, "matches": [{"ip_str": "1.1.1.1"}]}

    def _request(self, function, params):
        self.calls.append(
            {
                "method": "_request",
                "api_key": self.api_key,
                "function": function,
                "params": params,
            }
        )
        return {"total": 1, "matches": [{"ip_str": "1.1.1.1"}]}

def test_query_shodan_searches_with_options(monkeypatch):
    FakeShodanClient.calls = []
    monkeypatch.setattr(
        "cyberclip.userAction.ShodanAction.shodan.Shodan", FakeShodanClient
    )

    action = QueryShodanAction()
    action.conf = {"api_key": "token"}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "apache country:FR"},
        "Max results": {"type": "text", "value": "5"},
        "Facets": {"type": "fixedlist", "value": ["port"]},
        "Custom facets": {"type": "text", "value": "org"},
        "Fields": {"type": "fixedlist", "value": ["ip_str"]},
        "Custom fields": {"type": "text", "value": "port"},
        "Minify": {"type": "bool", "value": False},
    }

    result = action.execute()

    assert FakeShodanClient.calls == [
        {
            "method": "_request",
            "api_key": "token",
            "function": "/shodan/host/search",
            "params": {
                "query": "apache country:FR",
                "limit": 5,
                "facets": "port,org",
                "fields": "ip_str,port",
                "minify": False,
            },
        }
    ]
    assert result["query"] == "apache country:FR"
    assert result["fields"] == ["ip_str", "port"]
    assert result["response"]["matches"][0]["ip_str"] == "1.1.1.1"


def test_query_shodan_runs_multiple_newline_queries(monkeypatch):
    FakeShodanClient.calls = []
    monkeypatch.setattr(
        "cyberclip.userAction.ShodanAction.shodan.Shodan", FakeShodanClient
    )

    action = QueryShodanAction()
    action.conf = {"api_key": "token"}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "product:nginx\nport:22"},
        "Max results": {"type": "text", "value": "20"},
        "Facets": {"type": "fixedlist", "value": ["country"]},
        "Custom facets": {"type": "text", "value": ""},
        "Fields": {"type": "fixedlist", "value": []},
        "Custom fields": {"type": "text", "value": ""},
        "Minify": {"type": "bool", "value": True},
    }

    result = action.execute()

    assert [call["query"] for call in FakeShodanClient.calls] == [
        "product:nginx",
        "port:22",
    ]
    assert all(call["method"] == "search" for call in FakeShodanClient.calls)
    assert all(call["facets"] == ["country"] for call in FakeShodanClient.calls)
    assert result["product:nginx"]["query"] == "product:nginx"
    assert result["port:22"]["response"]["matches"][0]["ip_str"] == "1.1.1.1"


def test_query_shodan_requires_api_key():
    action = QueryShodanAction()
    action.conf = {}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "apache"},
        "Max results": {"type": "text", "value": "20"},
        "Facets": {"type": "fixedlist", "value": []},
        "Custom facets": {"type": "text", "value": ""},
        "Fields": {"type": "fixedlist", "value": []},
        "Custom fields": {"type": "text", "value": ""},
        "Minify": {"type": "bool", "value": True},
    }

    result = action.execute()

    assert result == {
        "error": "Missing Shodan API key. Configure SHODAN_API_KEY in .env"
    }

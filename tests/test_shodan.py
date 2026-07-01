from cyberclip.userAction.ShodanAction import (
    QueryShodanAction,
    ShodanDomainDNSAction,
    searchInShodanAction,
)


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

    def host(self, value):
        self.calls.append(
            {
                "method": "host",
                "api_key": self.api_key,
                "value": value,
            }
        )
        if isinstance(value, list):
            return [{"ip_str": ip, "ports": [443]} for ip in value]
        return {"ip_str": value, "ports": [443]}


class FakeParser:
    def __init__(self, parsertype, values):
        self.parsertype = parsertype
        self._values = values

    def extract(self):
        return self._values


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_query_shodan_searches_with_simple_options(monkeypatch):
    FakeShodanClient.calls = []
    monkeypatch.setattr(
        "cyberclip.userAction.ShodanAction.shodan.Shodan", FakeShodanClient
    )

    action = QueryShodanAction()
    action.conf = {"api_key": "token"}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "apache country:FR"},
        "Max results": {"type": "text", "value": "5"},
    }

    result = action.execute()

    assert FakeShodanClient.calls == [
        {
            "method": "search",
            "api_key": "token",
            "query": "apache country:FR",
            "page": 1,
            "limit": 5,
            "offset": None,
            "facets": None,
            "minify": True,
            "fields": None,
        }
    ]
    assert result["query"] == "apache country:FR"
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
    }

    result = action.execute()

    assert [call["query"] for call in FakeShodanClient.calls] == [
        "product:nginx",
        "port:22",
    ]
    assert all(call["method"] == "search" for call in FakeShodanClient.calls)
    assert result["product:nginx"]["query"] == "product:nginx"
    assert result["port:22"]["response"]["matches"][0]["ip_str"] == "1.1.1.1"


def test_query_shodan_requires_api_key():
    class DummyShodanClient:
        def __init__(self, api_key):
            self.api_key = api_key

    from cyberclip.userAction import ShodanAction as shodan_action_module

    shodan_action_module.shodan.Shodan = DummyShodanClient

    action = QueryShodanAction()
    action.conf = {}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "apache"},
        "Max results": {"type": "text", "value": "20"},
    }

    result = action.execute()

    assert result == {
        "error": "Missing Shodan API key. Configure SHODAN_API-KEY in .env"
    }


def test_search_shodan_ip_looks_up_each_ip(monkeypatch):
    FakeShodanClient.calls = []
    monkeypatch.setattr(
        "cyberclip.userAction.ShodanAction.shodan.Shodan", FakeShodanClient
    )

    action = searchInShodanAction(
        parsers={"ip": FakeParser("ip", ["8.8.8.8", "1.1.1.1"])}
    )
    action.conf = {"api_key": "token"}
    action.api = FakeShodanClient("token")

    result = action.execute()

    assert FakeShodanClient.calls == [
        {"method": "host", "api_key": "token", "value": "8.8.8.8"},
        {"method": "host", "api_key": "token", "value": "1.1.1.1"},
    ]
    assert result["8.8.8.8"]["ports"] == [443]
    assert result["1.1.1.1"]["ip_str"] == "1.1.1.1"


def test_search_shodan_bulk_returns_clear_error_on_unexpected_response(monkeypatch):
    class FakeBulkErrorClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def host(self, value):
            return {"error": "Corporate API required for bulk lookups"}

    monkeypatch.setattr(
        "cyberclip.userAction.ShodanAction.shodan.Shodan", FakeBulkErrorClient
    )

    action = searchInShodanAction(
        parsers={"ip": FakeParser("ip", ["8.8.8.8", "1.1.1.1"])}
    )
    action.api = FakeBulkErrorClient("token")
    action.complex_param = {
        "Allow bulk search": {"type": "boolean", "value": True},
        "Free account": {"type": "boolean", "value": False},
    }

    result = action.execute()

    assert result == {"error": "Corporate API required for bulk lookups"}


def test_search_shodan_bulk_handles_api_exception(monkeypatch):
    class FakeBulkExceptionClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def host(self, value):
            raise Exception("Access denied (403 Forbidden)")

    monkeypatch.setattr(
        "cyberclip.userAction.ShodanAction.shodan.Shodan", FakeBulkExceptionClient
    )

    action = searchInShodanAction(
        parsers={"ip": FakeParser("ip", ["8.8.8.8", "1.1.1.1"])}
    )
    action.api = FakeBulkExceptionClient("token")
    action.complex_param = {
        "Allow bulk search": {"type": "boolean", "value": True},
        "Free account": {"type": "boolean", "value": False},
    }

    result = action.execute()

    assert result == {"error": "Access denied (403 Forbidden)"}


def test_shodan_passive_dns_uses_domain_endpoint(monkeypatch):
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(
            {
                "url": url,
                "params": params,
                "timeout": timeout,
            }
        )
        return FakeResponse(
            {
                "domain": "example.com",
                "subdomains": ["www"],
                "data": [{"type": "A", "value": "1.2.3.4"}],
            }
        )

    monkeypatch.setattr("cyberclip.userAction.ShodanAction.requests.get", fake_get)

    action = ShodanDomainDNSAction(
        parsers={"domain": FakeParser("domain", ["example.com"])}
    )
    action.conf = {"api_key": "token"}
    action.complex_param = {
        "History": {"type": "bool", "value": True},
        "Type": {"type": "list", "value": "A", "choices": ["All", "A"]},
    }

    result = action.execute()

    assert calls == [
        {
            "url": "https://api.shodan.io/dns/domain/example.com",
            "params": {"key": "token", "history": "true", "type": "A"},
            "timeout": 20,
        }
    ]
    assert result["example.com"]["subdomains"] == ["www"]
    assert result["example.com"]["data"][0]["value"] == "1.2.3.4"

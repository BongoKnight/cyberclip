from cyberclip.userAction.ModatAction import QueryModatAction, SearchInModatAction


class FakeResponse:
    headers = {"content-type": "application/json"}
    status_code = 200
    reason = "OK"
    text = ""

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_query_modat_builds_bare_observable_queries():
    action = QueryModatAction()
    action.conf = {}

    assert action._build_query_from_user_input("example.com") == "domain=example.com"
    assert action._build_query_from_user_input("https://example.com/a") == (
        "domain=example.com"
    )
    assert action._build_query_from_user_input("1.1.1.1") == "ip=1.1.1.1"
    assert action._build_query_from_user_input("port=443") == "port=443"
    assert action._build_query_from_user_input("asn.org ~ 'Google'") == (
        "asn.org ~ 'Google'"
    )


def test_query_modat_derives_certificate_domains_for_ip_queries(monkeypatch):
    def fake_post(url, headers, json, timeout):
        return FakeResponse(
            {
                "page": [
                    {
                        "tls": {
                            "certificate": {
                                "subject_alt_name": [
                                    "www.example.com",
                                    "api.example.net",
                                ]
                            }
                        }
                    }
                ],
                "total_records": 1,
            }
        )

    monkeypatch.setattr("cyberclip.userAction.ModatAction.requests.post", fake_post)

    action = QueryModatAction()
    action.conf = {}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "1.1.1.1"},
        "Search target": {
            "type": "list",
            "choices": ["service", "host"],
            "value": "service",
        },
        "Max results": {"type": "text", "value": "20"},
    }

    result = action.execute()

    assert result["query"] == "ip=1.1.1.1"
    assert result["derived_domains_from_certificates"] == [
        "api.example.net",
        "www.example.com",
    ]


def test_query_modat_runs_multiple_newline_queries(monkeypatch):
    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append(json["query"])
        return FakeResponse({"page": [json["query"]], "total_records": 1})

    monkeypatch.setattr("cyberclip.userAction.ModatAction.requests.post", fake_post)

    action = QueryModatAction()
    action.conf = {}
    action.complex_param = {
        "Query": {"type": "longtext", "value": "example.com\nport=443\n1.1.1.1"},
        "Search target": {
            "type": "list",
            "choices": ["service", "host"],
            "value": "service",
        },
        "Max results": {"type": "text", "value": "20"},
    }

    result = action.execute()

    assert calls == ["domain=example.com", "port=443", "ip=1.1.1.1"]
    assert result["example.com"]["query"] == "domain=example.com"
    assert result["port=443"]["query"] == "port=443"
    assert result["1.1.1.1"]["query"] == "ip=1.1.1.1"


def test_query_modat_uses_selected_host_endpoint_and_trims(monkeypatch):
    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return FakeResponse({"page": list(range(12)), "total_records": 12})

    monkeypatch.setattr("cyberclip.userAction.ModatAction.requests.post", fake_post)

    action = QueryModatAction()
    action.conf = {}
    action.complex_param = {
        "Query": {"type": "text", "value": "example.com"},
        "Search target": {
            "type": "list",
            "choices": ["service", "host"],
            "value": "host",
        },
        "Max results": {"type": "text", "value": "5"},
    }

    result = action.execute()

    assert calls[0]["url"] == "https://api.magnify.modat.io/host/search/v1"
    assert calls[0]["json"] == {
        "query": "domain=example.com",
        "page": 1,
        "page_size": 10,
    }
    assert result["search_target"] == "host"
    assert result["response"]["page"] == [0, 1, 2, 3, 4]
    assert result["response"]["returned_records"] == 5


def test_modat_config_only_uses_api_key():
    action = SearchInModatAction()
    action.conf = {
        "base_url": "https://custom.example/",
        "service_search_path": "service/search/v2",
        "host-search-path": "/host/search/v2",
        "api_key": "token",
    }

    assert action._build_base_url() == "https://api.magnify.modat.io"
    assert action._build_search_path("service") == "/service/search/v1"
    assert action._build_search_path("host") == "/host/search/v1"
    assert action._build_headers()["Authorization"] == "token"

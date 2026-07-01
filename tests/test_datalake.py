from cyberclip.userAction.DatalakeAction import (
    QueryDatalakeAction,
    SearchInDatalakeAction,
)


class FakeParser:
    def __init__(self, parsertype, values):
        self.parsertype = parsertype
        self._values = values

    def extract(self):
        return self._values


class FakeResponse:
    def __init__(
        self,
        payload,
        *,
        status_code=200,
        reason="OK",
        headers=None,
        text=None,
    ):
        self.payload = payload
        self.status_code = status_code
        self.reason = reason
        self.headers = headers or {"content-type": "application/json"}
        self.text = text if text is not None else (
            payload if isinstance(payload, str) else ""
        )

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code} {self.reason}")
        return None

    def json(self):
        return self.payload


def test_search_datalake_auth_and_lookup(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(
            {
                "method": "POST",
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return FakeResponse({"access_token": "token", "refresh_token": "refresh"})

    def fake_get(url, headers=None, params=None, timeout=None):
        calls.append(
            {
                "method": "GET",
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        return FakeResponse({"atom_type": "domain", "atom_hits_count": 1})

    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.post", fake_post)
    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.get", fake_get)

    action = SearchInDatalakeAction(
        parsers={"domain": FakeParser("domain", ["example.com"])}
    )
    action.conf = {
        "email": "user@example.com",
        "password": "password",
        "base_url": "https://datalake.example/api",
    }

    result = action.execute()

    assert calls == [
        {
            "method": "POST",
            "url": "https://datalake.example/api/v3/auth/token/",
            "headers": {
                "accept": "application/json",
                "content-type": "application/json",
            },
            "json": {
                "email": "user@example.com",
                "password": "password",
            },
            "timeout": 20,
        },
        {
            "method": "GET",
            "url": "https://datalake.example/api/v3/mrti/threats/lookup/",
            "headers": {
                "accept": "application/json",
                "Authorization": "Token token",
            },
            "params": {
                "atom_type": "domain",
                "atom_value": "example.com",
                "hashkey_only": "false",
            },
            "timeout": 20,
        },
    ]
    assert result["example.com"]["atom_type"] == "domain"
    assert result["example.com"]["response"]["atom_hits_count"] == 1


def test_query_datalake_regexp_builds_advanced_payload(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        if url.endswith("/v3/auth/token/"):
            return FakeResponse({"access_token": "token"})
        if url.endswith("/v3/mrti/advanced-queries/threats/"):
            return FakeResponse({"count": 2, "results": [{"id": 1}, {"id": 2}]})
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.post", fake_post)

    action = QueryDatalakeAction()
    action.conf = {
        "email": "user@example.com",
        "password": "password",
        "base_url": "https://datalake.example/api",
    }
    action.complex_param = {
        "Query": {"type": "longtext", "value": "evil.*\nfoo.*"},
        "Query mode": {"type": "list", "value": "Regexp"},
        "Max results": {"type": "text", "value": "25"},
    }

    result = action.execute()

    assert calls[1] == {
        "url": "https://datalake.example/api/v3/mrti/advanced-queries/threats/",
        "headers": {
            "accept": "application/json",
            "Authorization": "Token token",
            "content-type": "application/json",
        },
        "json": {
            "limit": 25,
            "offset": 0,
            "query_body": {
                "AND": [
                    {
                        "AND": [
                            {
                                "field": "regexp",
                                "type": "search",
                                "multi_values": ["evil.*", "foo.*"],
                                "atom_values_only": True,
                            }
                        ]
                    }
                ]
            },
        },
        "timeout": 20,
    }
    assert result["response"]["count"] == 2


def test_query_datalake_threat_entity_builds_filter_payload(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        if url.endswith("/v3/auth/token/"):
            return FakeResponse({"access_token": "token"})
        if url.endswith("/v3/mrti/advanced-queries/threats/"):
            return FakeResponse({"count": 1, "results": [{"uid": "abc"}]})
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.post", fake_post)

    action = QueryDatalakeAction()
    action.conf = {
        "email": "user@example.com",
        "password": "password",
        "base_url": "https://datalake.example/api",
    }
    action.complex_param = {
        "Query": {"type": "longtext", "value": "12\n46"},
        "Query mode": {"type": "list", "value": "Threat entity"},
        "Max results": {"type": "text", "value": "10"},
    }

    result = action.execute()

    assert calls[1]["json"] == {
        "limit": 10,
        "offset": 0,
        "query_body": {
            "AND": [
                {
                    "AND": [
                            {
                                "field": "threat_entity",
                                "type": "filter",
                                "multi_values": [12, 46],
                            }
                    ]
                }
            ],
        },
    }
    assert result["query_mode"] == "threat_entity"
    assert result["response"]["results"][0]["uid"] == "abc"


def test_query_datalake_tags_builds_filter_payload(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        if url.endswith("/v3/auth/token/"):
            return FakeResponse({"access_token": "token"})
        if url.endswith("/v3/mrti/advanced-queries/threats/"):
            return FakeResponse({"count": 1, "results": [{"uid": "tag"}]})
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.post", fake_post)

    action = QueryDatalakeAction()
    action.conf = {
        "email": "user@example.com",
        "password": "password",
        "base_url": "https://datalake.example/api",
    }
    action.complex_param = {
        "Query": {"type": "longtext", "value": "runster\ngoat"},
        "Query mode": {"type": "list", "value": "Tags"},
        "Max results": {"type": "text", "value": "10"},
    }

    result = action.execute()

    assert calls[1]["json"]["query_body"]["AND"][0]["AND"][0] == {
        "field": "tags",
        "type": "filter",
        "multi_values": ["runster", "goat"],
    }
    assert result["query_mode"] == "tags"


def test_query_datalake_output_atom_types_builds_filter_payload(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        if url.endswith("/v3/auth/token/"):
            return FakeResponse({"access_token": "token"})
        if url.endswith("/v3/mrti/advanced-queries/threats/"):
            return FakeResponse({"count": 1, "results": [{"uid": "atom"}]})
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.post", fake_post)

    action = QueryDatalakeAction()
    action.conf = {
        "email": "user@example.com",
        "password": "password",
        "base_url": "https://datalake.example/api",
    }
    action.complex_param = {
        "Query": {"type": "longtext", "value": "39287"},
        "Query mode": {"type": "list", "value": "Threat entity ID"},
        "Output atom types": {
            "type": "fixedlist",
            "value": ["domain", "ip"],
        },
        "Max results": {"type": "text", "value": "10"},
    }

    result = action.execute()

    assert calls[1]["json"]["query_body"]["AND"][0]["AND"] == [
        {
            "field": "threat_entity",
            "type": "filter",
            "multi_values": [39287],
        },
        {
            "field": "atom_type",
            "type": "filter",
            "multi_values": ["domain", "ip"],
        },
    ]
    assert result["query_mode"] == "threat_entity"


def test_datalake_reauthenticates_once_when_access_token_expires(monkeypatch):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(
            {
                "method": "POST",
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return FakeResponse({"access_token": f"token-{len(calls)}"})

    get_calls = {"count": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        get_calls["count"] += 1
        calls.append(
            {
                "method": "GET",
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        if get_calls["count"] == 1:
            return FakeResponse(
                {"message": "Token has expired"},
                status_code=401,
                reason="UNAUTHORIZED",
            )
        return FakeResponse({"atom_type": "domain", "atom_hits_count": 1})

    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.post", fake_post)
    monkeypatch.setattr("cyberclip.userAction.DatalakeAction.requests.get", fake_get)

    action = SearchInDatalakeAction(
        parsers={"domain": FakeParser("domain", ["example.com"])}
    )
    action.conf = {
        "email": "user@example.com",
        "password": "password",
        "base_url": "https://datalake.example/api",
    }

    result = action.execute()

    assert result["example.com"]["response"]["atom_hits_count"] == 1
    assert calls[0]["url"].endswith("/v3/auth/token/")
    assert calls[1]["headers"]["Authorization"] == "Token token-1"
    assert calls[2]["url"].endswith("/v3/auth/token/")
    assert calls[3]["headers"]["Authorization"] == "Token token-3"

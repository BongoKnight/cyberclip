try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json
import ipaddress
import re
from collections.abc import Iterable
from urllib.parse import urlparse

import requests


DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "longtext", "value": "example.com"},
    "Search target": {
        "type": "list",
        "choices": ["service", "host"],
        "value": "service",
    },
    "Max results": {"type": "text", "value": "20"},
}

DEFAULT_SEARCH_PARAMETERS = {
    "Search target": {
        "type": "list",
        "choices": ["service", "host"],
        "value": "service",
    },
    "Max results": {"type": "text", "value": "20"},
}

DEFAULT_BASE_URL = "https://api.magnify.modat.io"
DEFAULT_SEARCH_TARGET = "service"
DEFAULT_SERVICE_SEARCH_PATH = "/service/search/v1"
DEFAULT_HOST_SEARCH_PATH = "/host/search/v1"
DEFAULT_SEARCH_PATHS = {
    "service": DEFAULT_SERVICE_SEARCH_PATH,
    "host": DEFAULT_HOST_SEARCH_PATH,
}


class _ModatMixin:
    domain_regex = re.compile(
        r"(?<![A-Za-z0-9-])(?:[A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}(?![A-Za-z0-9-])"
    )
    certificate_path_markers = (
        "cert",
        "certificate",
        "tls",
        "ssl",
        "x509",
        "san",
        "subject_alt_name",
        "issuer",
        "subject",
        "common_name",
        "server_name",
        "hostname",
        "domain",
    )
    structured_query_markers = ("=", "~", "<", ">", "|", "&", "(", ")", '"', "'")

    def _build_base_url(self) -> str:
        return DEFAULT_BASE_URL.rstrip("/")

    def _build_search_path(self, search_target: str = DEFAULT_SEARCH_TARGET) -> str:
        search_target = self._normalize_search_target(search_target)
        raw_path = DEFAULT_SEARCH_PATHS[search_target].strip()
        if not raw_path.startswith("/"):
            raw_path = f"/{raw_path}"
        return raw_path

    def _build_headers(self) -> dict[str, str]:
        headers = {"accept": "application/json"}
        api_key = self.conf.get("api-key") or self.conf.get("api_key") or ""
        if api_key:
            headers["Authorization"] = api_key
        return headers

    def _normalize_search_target(self, value) -> str:
        search_target = str(value or DEFAULT_SEARCH_TARGET).strip().lower()
        if search_target not in DEFAULT_SEARCH_PATHS:
            return DEFAULT_SEARCH_TARGET
        return search_target

    def _query_modat(
        self,
        query: str,
        page_size: int = 20,
        page: int = 1,
        search_target: str = DEFAULT_SEARCH_TARGET,
    ):
        search_target = self._normalize_search_target(search_target)
        url = f"{self._build_base_url()}{self._build_search_path(search_target)}"
        headers = self._build_headers()
        payload = {
            "query": query,
            "page": max(1, int(page)),
            "page_size": self._normalize_page_size(page_size),
        }
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(self._format_http_error(response, exc)) from exc
        content_type = response.headers.get("content-type", "")
        if "json" in content_type.lower():
            return response.json()
        return {"raw": response.text}

    def _trim_response_page(self, response, max_results: int):
        if not isinstance(response, dict):
            return response
        if "page" not in response or not isinstance(response["page"], list):
            return response

        trimmed = dict(response)
        # Modat enforces a minimum page_size of 10, so small UI limits are applied client-side after the API response is received.
        trimmed["page"] = response["page"][: max(1, max_results)]
        if "total_records" in trimmed:
            trimmed["returned_records"] = len(trimmed["page"])
        return trimmed

    def _format_http_error(self, response: requests.Response, exc: Exception) -> str:
        details = f"{response.status_code} {response.reason}"
        try:
            body = response.json()
        except Exception:
            body = response.text.strip()

        if body:
            if isinstance(body, (dict, list)):
                details = f"{details}: {json.dumps(body)}"
            else:
                details = f"{details}: {body}"
        return details

    def _normalize_result_limit(self, value, default: int = 20) -> int:
        try:
            limit = int(str(value).strip())
            return max(1, limit)
        except Exception:
            return default

    def _normalize_page_size(self, value, default: int = 20) -> int:
        try:
            size = int(str(value).strip())
        except Exception:
            size = default
        return min(100, max(10, size))

    def _walk_values(self, data, parent_path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                next_path = f"{parent_path}.{key}" if parent_path else str(key)
                yield next_path, value
                yield from self._walk_values(value, next_path)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                next_path = f"{parent_path}[{index}]"
                yield next_path, value
                yield from self._walk_values(value, next_path)

    def _extract_domains_from_string(self, value: str) -> set[str]:
        return {
            match.group(0).rstrip(".").lower()
            for match in self.domain_regex.finditer(value)
        }

    def _extract_domains_from_certificates(self, data) -> list[str]:
        domains = set()
        for path, value in self._walk_values(data):
            path_lower = path.lower()
            if not any(
                marker in path_lower for marker in self.certificate_path_markers
            ):
                continue

            if isinstance(value, str):
                domains.update(self._extract_domains_from_string(value))
            elif isinstance(value, Iterable) and not isinstance(
                value, (bytes, dict, str)
            ):
                for item in value:
                    if isinstance(item, str):
                        domains.update(self._extract_domains_from_string(item))

        return sorted(domains)

    def _wrap_response(
        self,
        query: str,
        response,
        derive_domains: bool = False,
        search_target: str = DEFAULT_SEARCH_TARGET,
    ) -> dict:
        result = {
            "query": query,
            "search_target": self._normalize_search_target(search_target),
            "response": response,
        }
        if derive_domains:
            result["derived_domains_from_certificates"] = (
                self._extract_domains_from_certificates(response)
            )
        return result

    def _build_observable_query(self, observable: str, observable_type: str) -> str:
        observable = self._normalize_observable_text(observable)
        if observable_type in {"ip", "ipv6"}:
            return f"ip={observable}"
        if observable_type == "domain":
            return f"domain={observable}"
        if observable_type == "url":
            hostname = self._extract_hostname(observable) or observable
            return f"domain={hostname}"
        return observable

    def _build_query_from_user_input(self, query: str) -> str:
        query = str(query or "").strip()
        if not query or self._is_structured_query(query):
            return query

        observable_type = self._detect_observable_type(query)
        if observable_type:
            return self._build_observable_query(query, observable_type)
        return query

    def _split_query_inputs(self, query: str) -> list[str]:
        return [line.strip() for line in str(query or "").splitlines() if line.strip()]

    def _should_derive_domains_for_query(self, query: str) -> bool:
        return str(query or "").strip().lower().startswith("ip=")

    def _detect_observable_type(self, value: str) -> str:
        normalized = self._normalize_observable_text(value)
        if self._looks_like_url(normalized):
            return "url"

        try:
            ipaddress.ip_address(normalized)
            return "ip"
        except ValueError:
            pass

        if self.domain_regex.fullmatch(normalized):
            return "domain"
        return ""

    def _is_structured_query(self, query: str) -> bool:
        if any(marker in query for marker in self.structured_query_markers):
            return True
        return any(char.isspace() for char in query)

    def _looks_like_url(self, value: str) -> bool:
        value_lower = value.lower()
        return value_lower.startswith(
            ("http://", "https://", "hxxp://", "hxxps://", "ftp://", "www.")
        )

    def _normalize_observable_text(self, value: str) -> str:
        return (
            str(value or "")
            .strip()
            .replace("[.]", ".")
            .replace("[://]", "://")
            .replace("hxxp://", "http://")
            .replace("hxxps://", "https://")
        )

    def _extract_hostname(self, value: str) -> str:
        normalized = self._normalize_observable_text(value)
        parsed = urlparse(normalized)
        if not parsed.netloc and normalized.lower().startswith("www."):
            parsed = urlparse(f"//{normalized}")
        return (parsed.hostname or "").strip(".").lower()


class SearchInModatAction(_ModatMixin, actionInterface):
    """Search observables in Modat Magnify.

    The action performs one query per IP, domain, or URL. For IP searches, it
    also tries to derive domain names from certificate-related fields returned
    by the API when they are present.

    Options:
    - Search target: "service" uses the current service search endpoint.
      "host" uses the host search endpoint.

    A Modat API key may be required depending on the endpoint and rate limits.
    """

    def __init__(
        self,
        parsers={},
        supportedType={"ip", "domain", "url"},
        complex_param=DEFAULT_SEARCH_PARAMETERS,
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Modat: Search IoC"
        self.indicators = "🔑"
        self.load_conf("Modat")

    def execute(self):
        self.results = {}
        self.observables = self.get_observables()
        observable_items = []
        for parser_type in self.supportedType:
            observable_items.extend(
                (parser_type, observable)
                for observable in self.observables.get(parser_type, [])
            )

        max_results = self._normalize_result_limit(self.get_param_value("Max results"))
        page_size = self._normalize_page_size(self.get_param_value("Max results"))
        search_target = self._normalize_search_target(
            self.get_param_value("Search target")
        )

        for observable_type, observable in sorted(set(observable_items)):
            try:
                query = self._build_observable_query(observable, observable_type)
                response = self._query_modat(
                    query, page_size=page_size, search_target=search_target
                )
                self.results[observable] = self._wrap_response(
                    query,
                    self._trim_response_page(response, max_results),
                    derive_domains=observable_type == "ip",
                    search_target=search_target,
                )
            except Exception as exc:
                self.results[observable] = {"query": observable, "error": str(exc)}
        return self.results

    def __str__(self):
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


class QueryModatAction(_ModatMixin, actionInterface):
    """Run an arbitrary Modat Magnify search query. Multiple independent queries can be sent by entering one query per line. A Modat API key may be required depending on the endpoint and rate limits.

    Options:
    - Search target: "service" uses the current service search endpoint.
      "host" uses the host search endpoint.


    Bare observables are normalized before being sent:
    - "1.1.1.1" becomes "ip=1.1.1.1"
    - "example.com" becomes "domain=example.com"
    - "https://example.com/path" becomes "domain=example.com"
    Existing Modat query syntax such as "port=443" or
    "asn.org ~ 'Google'" is sent unchanged.

    For IP queries, the action also tries to derive domain names from
    certificate-related fields returned by the API when they are present.
    """

    def __init__(
        self, parsers={}, supportedType={"text"}, complex_param=DEFAULT_QUERY_PARAMETERS
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Modat: Query"
        self.indicators = "🔑"
        self.load_conf("Modat")

    def execute(self):
        try:
            raw_queries = self._split_query_inputs(self.get_param_value("Query"))
            if not raw_queries:
                self.results = {"error": "No query provided"}
                return self.results

            max_results = self._normalize_result_limit(
                self.get_param_value("Max results")
            )
            page_size = self._normalize_page_size(self.get_param_value("Max results"))
            search_target = self._normalize_search_target(
                self.get_param_value("Search target")
            )

            if len(raw_queries) > 1:
                self.results = {}
                for raw_query in raw_queries:
                    try:
                        query = self._build_query_from_user_input(raw_query)
                        response = self._query_modat(
                            query, page_size=page_size, search_target=search_target
                        )
                        self.results[raw_query] = self._wrap_response(
                            query,
                            self._trim_response_page(response, max_results),
                            derive_domains=self._should_derive_domains_for_query(query),
                            search_target=search_target,
                        )
                    except Exception as exc:
                        self.results[raw_query] = {
                            "query": raw_query,
                            "search_target": search_target,
                            "error": str(exc),
                        }
                return self.results

            query = self._build_query_from_user_input(raw_queries[0])
            self.results = self._wrap_response(
                query,
                self._trim_response_page(
                    self._query_modat(
                        query, page_size=page_size, search_target=search_target
                    ),
                    max_results,
                ),
                derive_domains=self._should_derive_domains_for_query(query),
                search_target=search_target,
            )
        except Exception as exc:
            self.results = {"error": str(exc)}
        return self.results

    def __str__(self):
        self.execute()
        return json.dumps(self.results)

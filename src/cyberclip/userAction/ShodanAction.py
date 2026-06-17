try:
    from userAction.actionInterface import actionInterface
except ImportError:
    from actionInterface import actionInterface

import json
import time
from types import SimpleNamespace

import requests

try:
    import shodan
except ImportError:
    shodan = SimpleNamespace(Shodan=None)

"""Shodan actions for query, IP host lookup, and passive DNS enrichment."""


QUERY_PARAMETERS = {
    "Query": {"type": "longtext", "value": "apache"},
    "Max results": {"type": "text", "value": "20"},
}

SEARCH_IP_PARAMETERS = {
    "Allow bulk search": {"type": "bool", "value": False},
    "Free account": {"type": "bool", "value": False},
}

DOMAIN_DNS_PARAMETERS = {
    "History": {"type": "bool", "value": False},
    "Type": {
        "type": "list",
        "choices": ["All", "A", "AAAA", "CNAME", "NS", "SOA", "MX", "TXT"],
        "value": "All",
    },
}


class _ShodanMixin:
    def _get_api_key(self) -> str:
        api_key = self.conf.get("api_key", "")
        if not api_key:
            raise RuntimeError(
                "Missing Shodan API key. Configure SHODAN_API_KEY in .env"
            )
        return api_key

    def _build_client(self):
        if shodan.Shodan is None:
            raise RuntimeError(
                "Missing 'shodan' library. Install the shodan package to use this action."
            )
        return shodan.Shodan(self._get_api_key())

    def _normalize_result_limit(self, value, default: int = 20) -> int:
        try:
            limit = int(str(value).strip())
            return max(1, limit)
        except Exception:
            return default

    def _split_query_inputs(self, query: str) -> list[str]:
        return [line.strip() for line in str(query or "").splitlines() if line.strip()]

    def _wrap_response(self, query: str, response) -> dict:
        return {
            "query": query,
            "response": response,
        }

    def _request_json(self, path: str, params: dict | None = None) -> dict:
        api_key = self._get_api_key()
        query_params = {"key": api_key}
        if params:
            query_params.update(params)
        response = requests.get(
            f"https://api.shodan.io{path}",
            params=query_params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()


class QueryShodanAction(_ShodanMixin, actionInterface):
    """Run one or more Shodan search queries.

    The query field accepts plain text as well as standard Shodan search
    filters. Multiple queries can be sent by writing one query per line.
    """

    def __init__(
        self, parsers={}, supportedType={"text"}, complex_param=QUERY_PARAMETERS
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Shodan: Query"
        self.indicators = "🔑"
        self.load_conf("Shodan")

    def execute(self):
        try:
            queries = self._split_query_inputs(self.get_param_value("Query"))
            if not queries:
                self.results = {"error": "No query provided"}
                return self.results

            api = self._build_client()
            limit = self._normalize_result_limit(self.get_param_value("Max results"))

            if len(queries) == 1:
                query = queries[0]
                response = api.search(query, limit=limit, minify=True)
                self.results = self._wrap_response(query, response)
                return self.results

            self.results = {}
            for query in queries:
                try:
                    response = api.search(query, limit=limit, minify=True)
                    self.results[query] = self._wrap_response(query, response)
                except Exception as exc:
                    self.results[query] = {"query": query, "error": str(exc)}
            return self.results
        except Exception as exc:
            self.results = {"error": str(exc)}
            return self.results

    def __str__(self):
        self.execute()
        return json.dumps(self.results)


class searchInShodanAction(actionInterface):
    r"""Search IP addresses using the Shodan API.

    Queries Shodan for detailed information about IP addresses including open
    ports, services, vulnerabilities, and banners. Rate-limits requests for
    free accounts.

    Supported Types:
        ip

    Configuration:
        Requires the following in ``.env``::

            Shodan:
            - API_KEY: <your Shodan API key>

    Network Activity:
        Makes requests to: api.shodan.io

    Action Options:
        Allow bulk search (boolean): Use bulk search API (requires paid plan).
            Default: False
        Free account (boolean): Add 1-second delay between requests to avoid
            rate limits on free accounts.
            Default: False

    Example:
        >>> from userTypeParser.IPParser import ipv4Parser
        >>> parser = ipv4Parser("8.8.8.8")
        >>> action = searchInShodanAction({"ip": parser})
        >>> results = action.execute()
        >>> print(results.get("8.8.8.8", {}).get("org"))
        Google LLC

    Note:
        Free accounts have rate limits. Enable "Free account" parameter to
        automatically wait 1 second between requests.
    """

    def __init__(
        self,
        parsers={},
        supportedType={"ip"},
        complex_param={
            "Allow bulk search": {"type": "boolean", "value": False},
            "Free account": {"type": "boolean", "value": False},
        },
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Shodan: Search IP"
        self.indicators = "🔑"
        self.load_conf("Shodan")
        if shodan.Shodan is not None and self.conf.get("api_key", ""):
            self.api = shodan.Shodan(self.conf.get("api_key", ""))
        else:
            self.api = None

    def execute(self) -> object:
        """Execute Shodan lookups on all parsed IP observables.

        Queries Shodan API for each IP with rate limiting if configured.

        Returns:
            dict[str, dict]: Keys are IP addresses, values are Shodan host
                information dictionaries.
        """
        self.results = {}
        self.observables = self.get_observables()
        if self.api:
            if self.observables.get("ip"):
                if not self.get_param_value("Allow bulk search"):
                    for ip in self.observables.get("ip"):
                        try:
                            self.results[ip] = self.api.host(ip)
                            if self.get_param_value("Free account"):
                                time.sleep(1.1)
                        except:
                            pass
                else:
                    try:
                        data = self.api.host(self.observables.get("ip"))
                    except Exception as e:
                        self.results = {"error": str(e)}
                        return self.results
                    if isinstance(data, list):
                        for info in data:
                            if isinstance(info, dict) and info.get("ip_str"):
                                self.results[info["ip_str"]] = info
                        if self.results:
                            return self.results
                    if isinstance(data, dict) and data.get("error"):
                        return {"error": str(data.get("error"))}
                    return {
                        "error": (
                            "Bulk Shodan host lookups require a Corporate API plan "
                            "or returned an unexpected response."
                        )
                    }
        return self.results

    def __str__(self) -> str:
        """Return human-readable representation of Shodan results.

        Calls :meth:`execute` and formats output as JSON per IP.

        Returns:
            str: JSON-formatted Shodan data, one IP per line.
        """
        self.execute()
        if isinstance(self.results, dict) and "error" in self.results:
            return json.dumps(self.results)
        return "\n".join(f"{json.dumps(v)}" for k, v in self.results.items())


class ShodanDomainDNSAction(_ShodanMixin, actionInterface):
    r"""Retrieve passive DNS information for domains from Shodan.

    Uses the ``/dns/domain/{domain}`` endpoint to fetch observed subdomains and
    DNS entries from Shodan's dataset.
    """

    def __init__(
        self,
        parsers={},
        supportedType={"domain"},
        complex_param=DOMAIN_DNS_PARAMETERS,
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Shodan: Passive DNS"
        self.indicators = "🔑"
        self.load_conf("Shodan")

    def _normalize_history(self, value) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

    def _normalize_record_type(self, value: str) -> str | None:
        normalized = str(value or "").strip().upper()
        if not normalized or normalized == "ALL":
            return None
        return normalized

    def execute(self):
        self.results = {}
        try:
            domains = self.get_observables().get("domain", [])
            if not domains:
                return self.results

            history = self._normalize_history(self.get_param_value("History"))
            record_type = self._normalize_record_type(self.get_param_value("Type"))
            params = {"history": str(history).lower()}
            if record_type:
                params["type"] = record_type

            for domain in domains:
                try:
                    self.results[domain] = self._request_json(
                        f"/dns/domain/{domain}",
                        params=params,
                    )
                except Exception as exc:
                    self.results[domain] = {"error": str(exc)}
            return self.results
        except Exception as exc:
            self.results = {"error": str(exc)}
            return self.results

    def __str__(self) -> str:
        self.execute()
        if isinstance(self.results, dict) and "error" in self.results:
            return json.dumps(self.results)
        return "\n".join(
            f"{domain}\t{json.dumps(result)}" for domain, result in self.results.items()
        )


if __name__ == "__main__":
    print(str(QueryShodanAction()))

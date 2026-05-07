try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json
import time

import shodan
from shodan.helpers import create_facet_string

"""A action module, to open search observables contained in a text in Shodan."""


SHODAN_FACET_CHOICES = [
    "asn",
    "ip",
    "city",
    "country",
    "domain",
    "has_screenshot",
    "isp",
    "link",
    "org",
    "os",
    "port",
    "postal",
    "product",
    "region",
    "ssl.cert.alg",
    "ssl.cert.expired",
    "ssl.cert.fingerprint",
    "ssl.cert.issuer.cn",
    "ssl.cert.pubkey.bits",
    "ssl.cert.serial",
    "ssl.cert.subject.cn",
    "tag",
    "timestamp",
    "transport",
    "version",
    "vuln",
]

SHODAN_FIELD_CHOICES = [
    "ip_str",
    "port",
    "org",
    "isp",
    "asn",
    "hostnames",
    "domains",
    "transport",
    "product",
    "version",
    "os",
    "timestamp",
    "data",
    "location.country_code",
    "location.country_name",
    "location.city",
    "location.region_code",
    "location.latitude",
    "location.longitude",
    "ssl.cert.subject.cn",
    "ssl.cert.issuer.cn",
    "ssl.cert.serial",
    "ssl.cert.fingerprint.sha256",
    "ssl.cert.expired",
    "http.title",
    "http.html_hash",
    "http.favicon.hash",
    "opts.raw",
]

DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "longtext", "value": "apache"},
    "Max results": {"type": "text", "value": "20"},
    "Facets": {
        "type": "fixedlist",
        "choices": SHODAN_FACET_CHOICES,
        "value": [],
    },
    "Custom facets": {"type": "text", "value": ""},
    "Fields": {
        "type": "fixedlist",
        "choices": SHODAN_FIELD_CHOICES,
        "value": [],
    },
    "Custom fields": {"type": "text", "value": ""},
    "Minify": {"type": "bool", "value": True},
}


class _ShodanMixin:
    def _build_client(self):
        if getattr(self, "api", None):
            return self.api
        api_key = self.conf.get("api_key", "")
        if not api_key:
            raise RuntimeError(
                "Missing Shodan API key. Configure SHODAN_API_KEY in .env"
            )
        self.api = shodan.Shodan(api_key)
        return self.api

    def _normalize_result_limit(self, value, default: int = 20) -> int:
        try:
            limit = int(str(value).strip())
            return max(1, limit)
        except Exception:
            return default

    def _normalize_csv_parameter(self, value):
        if isinstance(value, (list, tuple, set)):
            items = [str(item).strip() for item in value]
        else:
            items = str(value or "").split(",")
            items = [item.strip() for item in items]
        return [item for item in items if item]

    def _normalize_combined_csv_parameter(self, *values):
        items = []
        seen = set()
        for value in values:
            normalized = self._normalize_csv_parameter(value)
            if not normalized:
                continue
            for item in normalized:
                if item and item not in seen:
                    seen.add(item)
                    items.append(item)
        return items or None

    def _normalize_bool(self, value) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

    def _split_query_inputs(self, query: str) -> list[str]:
        return [line.strip() for line in str(query or "").splitlines() if line.strip()]

    def _query_shodan(
        self,
        query: str,
        limit: int = 20,
        facets=None,
        fields=None,
        minify: bool = True,
    ):
        api = self._build_client()
        if fields:
            args = {
                "query": query,
                "limit": limit,
                "fields": ",".join(fields),
                "minify": False,
            }
            if facets:
                args["facets"] = create_facet_string(facets)
            return api._request("/shodan/host/search", args)
        return api.search(
            query,
            limit=limit,
            facets=facets,
            minify=bool(minify),
        )

    def _wrap_response(
        self,
        query: str,
        response,
        facets=None,
        fields=None,
        minify: bool = True,
    ) -> dict:
        result = {
            "query": query,
            "response": response,
        }
        if facets:
            result["facets"] = facets
        if fields:
            result["fields"] = fields
        if not fields:
            result["minify"] = bool(minify)
        return result


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

    Parameters:
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
        >>> print(results["8.8.8.8"]["org"])
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
        if self.conf.get("api_key", ""):
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
                    data = self.api.host(self.observables.get("ip"))
                    for info in data:
                        self.results[info["ip_str"]] = info
        return self.results

    def __str__(self):
        """Return human-readable representation of Shodan results.

        Calls :meth:`execute` and formats output as JSON per IP.

        Returns:
            str: JSON-formatted Shodan data, one IP per line.
        """
        self.execute()
        return "\n".join(f"{json.dumps(v)}" for k, v in self.results.items())


class QueryShodanAction(_ShodanMixin, actionInterface):
    """Run arbitrary Shodan search queries.

    Multiple independent queries can be sent by entering one query per line.
    A Shodan API key is required.
    """

    def __init__(
        self, parsers={}, supportedType={"text"}, complex_param=DEFAULT_QUERY_PARAMETERS
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Shodan: Query"
        self.indicators = "🔑"
        self.load_conf("Shodan")

    def execute(self):
        try:
            raw_queries = self._split_query_inputs(self.get_param_value("Query"))
            if not raw_queries:
                self.results = {"error": "No query provided"}
                return self.results

            limit = self._normalize_result_limit(self.get_param_value("Max results"))
            facets = self._normalize_combined_csv_parameter(
                self.get_param_value("Facets"),
                self.get_param_value("Custom facets"),
            )
            fields = self._normalize_combined_csv_parameter(
                self.get_param_value("Fields"),
                self.get_param_value("Custom fields"),
            )
            minify = self._normalize_bool(self.get_param_value("Minify"))

            if len(raw_queries) > 1:
                self.results = {}
                for query in raw_queries:
                    try:
                        response = self._query_shodan(
                            query,
                            limit=limit,
                            facets=facets,
                            fields=fields,
                            minify=minify,
                        )
                        self.results[query] = self._wrap_response(
                            query,
                            response,
                            facets=facets,
                            fields=fields,
                            minify=minify,
                        )
                    except Exception as exc:
                        self.results[query] = {"query": query, "error": str(exc)}
                return self.results

            query = raw_queries[0]
            response = self._query_shodan(
                query,
                limit=limit,
                facets=facets,
                fields=fields,
                minify=minify,
            )
            self.results = self._wrap_response(
                query,
                response,
                facets=facets,
                fields=fields,
                minify=minify,
            )
        except Exception as exc:
            self.results = {"error": str(exc)}
        return self.results

    def __str__(self):
        self.execute()
        return json.dumps(self.results)


if __name__ == "__main__":
    from userTypeParser.IPParser import ipv4Parser

    data = (
        "127.0.0.1, 206.168.89.216, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    )
    parser = ipv4Parser(data)
    a = str(searchInShodanAction({"ip": parser}, ["ip"]))
    b = str(QueryShodanAction())
    print(a, b, parser.extract())

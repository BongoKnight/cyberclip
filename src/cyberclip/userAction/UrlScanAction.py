try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import urllib.parse
import requests
import json
import urllib

BASE_SEARCH_URL = "https://urlscan.io/api/v1/search/"


class SearchInUrlScanAction(actionInterface):
    """An action module to search IP and domains on URLScan. This action runs a search query per observable and returns up to 20 results for each IP, domain, or analytics value."""

    def __init__(self, parsers={}, supportedType={"ip", "domain", "analytics"}):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "UrlScan: Search IoC"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("api-key", "")
        self.headers = {"accept": "application/json"}
        if API_KEY:
            self.headers["API-Key"] = API_KEY

    def execute(self) -> object:
        self.results = {}
        observables = []
        self.observables = self.get_observables()
        for parsertype in self.supportedType:
            observables += self.observables.get(parsertype, [])
        for observable in set(observables):
            try:
                query_url = (
                    BASE_SEARCH_URL + f"?q={urllib.parse.quote(observable)}&size=20"
                )
                response = requests.get(query_url, headers=self.headers, timeout=15)
                response.raise_for_status()
                self.results.update({observable: response.json()})
            except Exception as e:
                self.results.update({observable: str(e)})
        return self.results

    def __str__(self):
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "text", "value": "*"},
    "Max results": {"type": "text", "value": "20"},
    "Result mode": {"type": "bool", "value": False},
    "Include DOM": {"type": "bool", "value": False},
}


class QueryUrlScanAction(actionInterface):
    """An action module to query the URLScan API. An API key may be required depending on the query and rate limits.

    Use this action to retrieve either standard search results or detailed results for matching scans.

    Options:
    - Result mode: return detailed scan results instead of search results
    - Include DOM: also fetch the DOM snapshot for each matching scan
    """

    def __init__(
        self, parsers={}, supportedType={"text"}, complex_param=DEFAULT_QUERY_PARAMETERS
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "UrlScan: Query"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("api-key", "")
        self.headers = {"accept": "application/json"}
        if API_KEY:
            self.headers["API-Key"] = API_KEY
        self._dom_cache = {}
        self._result_cache = {}

    def _extract_scan_ids(self, search_json):

        its = search_json.get("results", [])
        scan_ids = []

        for it in its:

            sid = None

            result_url = it.get("result")

            if result_url and "/api/v1/result/" in result_url:
                sid = result_url.split("/api/v1/result/")[1].strip("/")

            if not sid:
                sid = it.get("_id")

            if not sid:
                task = it.get("task", {})
                if isinstance(task, dict):
                    sid = task.get("uuid")

            if sid:
                scan_ids.append(sid)

        # remove duplicates while preserving order
        seen = set()
        unique_scan_ids = []

        for sid in scan_ids:
            if sid not in seen:
                seen.add(sid)
                unique_scan_ids.append(sid)

        return unique_scan_ids

    def _fetch_result(self, scan_id):
        if scan_id in self._result_cache:
            return self._result_cache[scan_id]

        url = f"https://urlscan.io/api/v1/result/{scan_id}/"

        r = requests.get(url, headers=self.headers, timeout=15)
        r.raise_for_status()

        data = r.json()

        self._result_cache[scan_id] = data

        return data

    def _fetch_dom(self, scan_id: str) -> str:
        """Fetch DOM snapshot text for a given urlscan scanId."""
        if scan_id in self._dom_cache:
            return self._dom_cache[scan_id]
        dom_url = f"https://urlscan.io/dom/{scan_id}/"
        r = requests.get(dom_url, headers=self.headers, timeout=15)
        r.raise_for_status()
        dom = r.text
        self._dom_cache[scan_id] = dom
        return dom

    def execute(self):
        self.results = {}
        try:
            query = self.get_param_value("Query")
            limit = (
                int(self.get_param_value("Max results"))
                if str(self.get_param_value("Max results")).isdecimal()
                else 20
            )
            result_mode = bool(self.get_param_value("Result mode"))
            include_dom = bool(self.get_param_value("Include DOM"))
            if not (result_mode):
                query_url = (
                    BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}&size={limit}"
                )
                response = requests.get(query_url, headers=self.headers, timeout=15)
                response.raise_for_status()
                self.results = response.json()
                if include_dom:
                    scan_ids = self._extract_scan_ids(self.results)
                    dom_map = {}
                    for sid in scan_ids[:limit]:
                        try:
                            dom_map[sid] = self._fetch_dom(sid)
                        except Exception as e:
                            dom_map[sid] = f"ERROR: {e}"
                    self.results["_dom"] = dom_map

            else:
                search_url = (
                    BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}&size={limit}"
                )
                search_response = requests.get(
                    search_url, headers=self.headers, timeout=15
                )
                search_response.raise_for_status()
                search_json = search_response.json()
                scan_ids = self._extract_scan_ids(search_json)
                results = []

                for sid in scan_ids[:limit]:
                    try:
                        entry = {"scanId": sid, "result": self._fetch_result(sid)}
                        if include_dom:
                            try:
                                entry["dom"] = self._fetch_dom(sid)
                            except Exception as e:
                                entry["dom_error"] = str(e)
                        results.append(entry)
                    except Exception as e:
                        results.append({"scanId": sid, "error": str(e)})

                self.results = results

        except Exception as e:
            self.results = {"error": str(e)}
        return self.results

    def __str__(self):
        self.execute()
        return json.dumps(self.results)


if __name__ == "__main__":
    from userTypeParser.domainParser import domainParser

    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain": parser}, ["domain"]))
    b = str(QueryUrlScanAction())
    print(b, parser.objects)

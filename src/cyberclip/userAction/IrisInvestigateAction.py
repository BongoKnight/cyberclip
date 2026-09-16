try:
    from userAction.actionInterface import actionInterface
except Exception:
    from actionInterface import actionInterface

import json
import urllib
import urllib.parse

import requests

IRIS_INVESTIGATE_URL = "https://api.domaintools.com/v1/iris-investigate/"


class SearchDomainInDomainToolsAction(actionInterface):
    """An action module to search domains on DomainTools Iris. This action runs a search query per group of 100 domains and returns raw JSON data."""

    def __init__(self, parsers={}, supportedType={"domain"}):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "DomainTools Iris: Search Domain"
        self.indicators = "🔑"
        self.load_conf("iris")
        API_KEY = self.conf.get("api_key", "")
        USERNAME = self.conf.get("username", "")
        self.headers = {}
        if API_KEY:
            self.headers["X-Api-Key"] = API_KEY
        if USERNAME:
            self.headers["api_username"] = USERNAME

    def execute(self) -> object:
        self.results = {}
        observables = []
        self.observables = self.get_observables()
        observables += self.observables.get("domain", [])
        try:
            query_url = IRIS_INVESTIGATE_URL + f"?domain={",".join(observables)}&format=json"
            response = requests.post(query_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            if response.status_code == 200:
                for entry in response.json().get("response").get("results"):
                    self.results.update({entry["domain"]: entry})
        except Exception as e:
            self.results = {"error":str(e) + str(self.headers)}
        return self.results

    def __str__(self) -> str:
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


# DEFAULT_QUERY_PARAMETERS = {
#     "Query": {"type": "text", "value": "*"},
#     "Max results": {"type": "text", "value": "20"},
#     "Result mode": {"type": "bool", "value": False},
#     "Include DOM": {"type": "bool", "value": False},
# }


# class QueryUrlScanAction(actionInterface):
#     """An action module to query the URLScan API. An API key may be required depending on the query and rate limits.

#     Use this action to retrieve either standard search results or detailed results for matching scans.

#     Options:
#     - Result mode: return detailed scan results instead of search results
#     - Include DOM: also fetch the DOM snapshot for each matching scan
#     """

#     def __init__(
#         self, parsers={}, supportedType={"text"}, complex_param=DEFAULT_QUERY_PARAMETERS
#     ):
#         super().__init__(
#             parsers=parsers, supportedType=supportedType, complex_param=complex_param
#         )
#         self.description = "UrlScan: Query"
#         self.indicators = "🔑"
#         self.load_conf("UrlScan")
#         API_KEY = self.conf.get("api_key", "")
#         self.headers = {"accept": "application/json"}
#         if API_KEY:
#             self.headers["API-Key"] = API_KEY
#         self._dom_cache = {}
#         self._result_cache = {}

#     def _extract_scan_ids(self, search_json):
#         its = search_json.get("results", [])
#         scan_ids = []

#         for it in its:
#             sid = None
#             result_url = it.get("result")

#             if result_url and "/api/v1/result/" in result_url:
#                 sid = result_url.split("/api/v1/result/")[1].strip("/")

#             if not sid:
#                 sid = it.get("_id")

#             if not sid:
#                 task = it.get("task", {})
#                 if isinstance(task, dict):
#                     sid = task.get("uuid")

#             if sid:
#                 scan_ids.append(sid)

#         seen = set()
#         unique_scan_ids = []
#         for sid in scan_ids:
#             if sid not in seen:
#                 seen.add(sid)
#                 unique_scan_ids.append(sid)

#         return unique_scan_ids

#     def _fetch_result(self, scan_id):
#         if scan_id in self._result_cache:
#             return self._result_cache[scan_id]

#         url = f"https://urlscan.io/api/v1/result/{scan_id}/"
#         response = requests.get(url, headers=self.headers, timeout=15)
#         response.raise_for_status()

#         data = response.json()
#         self._result_cache[scan_id] = data
#         return data

#     def _fetch_dom(self, scan_id: str) -> str:
#         """Fetch DOM snapshot text for a given urlscan scanId."""
#         if scan_id in self._dom_cache:
#             return self._dom_cache[scan_id]
#         dom_url = f"https://urlscan.io/dom/{scan_id}/"
#         response = requests.get(dom_url, headers=self.headers, timeout=15)
#         response.raise_for_status()
#         dom = response.text
#         self._dom_cache[scan_id] = dom
#         return dom

#     def execute(self) -> dict[str, dict | str]:
#         self.results = {}
#         try:
#             query = self.get_param_value("Query")
#             limit = (
#                 int(self.get_param_value("Max results"))
#                 if str(self.get_param_value("Max results")).isdecimal()
#                 else 20
#             )
#             result_mode = bool(self.get_param_value("Result mode"))
#             include_dom = bool(self.get_param_value("Include DOM"))
#             if not result_mode:
#                 query_url = (
#                     BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}&size={limit}"
#                 )
#                 response = requests.get(query_url, headers=self.headers, timeout=15)
#                 response.raise_for_status()
#                 self.results = response.json()
#                 if include_dom:
#                     scan_ids = self._extract_scan_ids(self.results)
#                     dom_map = {}
#                     for sid in scan_ids[:limit]:
#                         try:
#                             dom_map[sid] = self._fetch_dom(sid)
#                         except Exception as e:
#                             dom_map[sid] = f"ERROR: {e}"
#                     self.results["_dom"] = dom_map
#             else:
#                 search_url = (
#                     BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}&size={limit}"
#                 )
#                 search_response = requests.get(
#                     search_url, headers=self.headers, timeout=15
#                 )
#                 search_response.raise_for_status()
#                 search_json = search_response.json()
#                 scan_ids = self._extract_scan_ids(search_json)
#                 results = []

#                 for sid in scan_ids[:limit]:
#                     try:
#                         entry = {"scanId": sid, "result": self._fetch_result(sid)}
#                         if include_dom:
#                             try:
#                                 entry["dom"] = self._fetch_dom(sid)
#                             except Exception as e:
#                                 entry["dom_error"] = str(e)
#                         results.append(entry)
#                     except Exception as e:
#                         results.append({"scanId": sid, "error": str(e)})

#                 self.results = results
#         except Exception as e:
#             self.results = {"error": str(e)}
#         return self.results

#     def __str__(self) -> str:
#         self.execute()
#         return json.dumps(self.results)


# class ResultFromUrlScanAction(actionInterface):
#     r"""Retrieve full scan results from URLScan.io result URLs.

#     Fetches complete scan data from URLScan result API endpoints. Only
#     processes URLs starting with ``https://urlscan.io/api/v1/result/``.

#     Supported Types:
#         url

#     Configuration:
#         Requires the following in ``.env``::

#             UrlScan:
#             - api_key: <your URLScan.io API key>

#     Network Activity:
#         Makes requests to: urlscan.io/api/v1/result/*

#     Example:
#         >>> from userTypeParser.URLParser import URLParser
#         >>> url = "https://urlscan.io/api/v1/result/abc12345-1234-1234-1234-123456789abc/"
#         >>> parser = URLParser(url)
#         >>> action = ResultFromUrlScanAction({"url": parser})
#         >>> results = action.execute()
#         >>> print(results.get(url, {}).get("page", {}).get("domain"))
#         example.com
#     """

#     def __init__(self, parsers={}, supportedType={"url"}):
#         super().__init__(parsers=parsers, supportedType=supportedType)
#         self.description = "UrlScan: Get full results"
#         self.indicators = "🔑"
#         self.load_conf("UrlScan")
#         API_KEY = self.conf.get("api_key", "")
#         self.headers = {"accept": "application/json", "API-Key": API_KEY}

#     def execute(self) -> dict[str, dict | str]:
#         """Execute result fetching on all parsed URLScan result URLs.

#         Fetches full scan data from each valid result URL.

#         Returns:
#             dict[str, dict]: Keys are result URLs, values are complete scan
#                 result JSON or error dicts.
#         """
#         self.results = {}
#         try:
#             result_urls = self.get_observables().get("url", [])
#             for url in result_urls:
#                 if url.startswith("https://urlscan.io/api/v1/result/"):
#                     try:
#                         response = requests.get(url, headers=self.headers)
#                         self.results[url] = response.json()
#                     except Exception as e:
#                         self.results = {"error": str(e)}
#         except Exception:
#             pass
#         return self.results

#     def __str__(self) -> str:
#         """Return human-readable representation of scan results.

#         Calls :meth:`execute` and formats output as JSON array.

#         Returns:
#             str: JSON array of all scan results.
#         """
#         self.execute()
#         return json.dumps([response for response in self.results.values()])


if __name__ == "__main__":
    from userTypeParser.domainParser import domainParser

    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain": parser}, ["domain"]))
    b = str(QueryUrlScanAction())
    print(b, parser.objects)

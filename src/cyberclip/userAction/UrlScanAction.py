try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import json
import urllib
import urllib.parse

import requests

BASE_SEARCH_URL = "https://urlscan.io/api/v1/search/"


class SearchInUrlScanAction(actionInterface):
    r"""Search for IPs, domains, and analytics IDs on URLScan.io.

    Queries the URLScan.io search API to find scans containing the specified
    observables. Returns up to 20 results per observable.

    Supported Types:
        ip, domain, analytics

    Configuration:
        Requires the following in ``.env``::

            UrlScan:
            - API_KEY: <your URLScan.io API key>

    Network Activity:
        Makes requests to: urlscan.io/api/v1/search

    Example:
        ```python
        from userTypeParser.domainParser import domainParser
        parser = domainParser("example.com")
        action = SearchInUrlScanAction({"domain": parser})
        results = action.execute()
        print(results["example.com"]["total"])
        42
        ```
    """

    def __init__(self, parsers={}, supportedType={"ip", "domain", "analytics"}):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "UrlScan: Search IoC"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("API_KEY", "")
        self.headers = {"accept": "application/json", "API-Key": API_KEY}

    def execute(self) -> object:
        """Execute URLScan searches on all parsed observables.

        Queries URLScan API for each IP, domain, or analytics ID.

        Returns:
            dict[str, dict | str]: Keys are observables, values are URLScan
                search result JSON or error messages.
        """
        self.results = {}
        observables = []
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            try:
                query_url = BASE_SEARCH_URL + f"?q={observable}&size=20"
                response = requests.get(query_url, headers=self.headers)
                self.results.update({observable: response.json()})
            except Exception as e:
                self.results.update({observable: str(e)})
        return self.results

    def __str__(self):
        """Return human-readable representation of search results.

        Calls :meth:`execute` and formats output as JSON per observable.

        Returns:
            str: JSON-formatted search results, one per line.
        """
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "text", "value": "*"},
    "Max results": {"type": "text", "value": "20"},
}


class QueryUrlScanAction(actionInterface):
    r"""Query URLScan.io with custom search queries.

    Performs custom search queries against the URLScan.io database using their
    search syntax. Supports filtering by domain, IP, page content, and more.

    Supported Types:
        text

    Configuration:
        Requires the following in ``.env``::

            UrlScan:
            - API_KEY: <your URLScan.io API key>

    Network Activity:
        Makes requests to: urlscan.io/api/v1/search

    Parameters:
        Query (text): URLScan search query.
            Examples: "domain:example.com", "page.ip:8.8.8.8", "*"
            Default: *
        Max results (text): Maximum number of results to return.
            Default: 20

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("domain:example.com")
        >>> action = QueryUrlScanAction({"text": parser})
        >>> action.complex_param["Query"]["value"] = "domain:example.com"
        >>> results = action.execute()
        >>> print(results["total"])
        42

    Note:
        Query syntax: https://urlscan.io/docs/search/
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
        API_KEY = self.conf.get("API_KEY", "")
        self.headers = {"accept": "application/json", "API-Key": API_KEY}

    def execute(self):
        """Execute custom URLScan query.

        Sends configured query to URLScan API with result limit.

        Returns:
            dict: URLScan search result JSON or error dict.
        """
        self.results = {}
        try:
            query = self.get_param_value("Query")
            limit = (
                int(self.get_param_value("Max results"))
                if str(self.get_param_value("Max results")).isdecimal()
                else 20
            )
            query_url = BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}&size={limit}"
            response = requests.get(query_url, headers=self.headers)
            self.results = response.json()
        except Exception as e:
            self.results = {"error": str(e)}
        return self.results

    def __str__(self):
        """Return human-readable representation of query results.

        Calls :meth:`execute` and formats output as indented JSON.

        Returns:
            str: JSON-formatted query results.
        """
        self.execute()
        return json.dumps(self.results)


class ResultFromUrlScanAction(actionInterface):
    r"""Retrieve full scan results from URLScan.io result URLs.

    Fetches complete scan data from URLScan result API endpoints. Only
    processes URLs starting with ``https://urlscan.io/api/v1/result/``.

    Supported Types:
        url

    Configuration:
        Requires the following in ``.env``::

            UrlScan:
            - API_KEY: <your URLScan.io API key>

    Network Activity:
        Makes requests to: urlscan.io/api/v1/result/*

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> url = "https://urlscan.io/api/v1/result/abc12345-1234-1234-1234-123456789abc/"
        >>> parser = URLParser(url)
        >>> action = ResultFromUrlScanAction({"url": parser})
        >>> results = action.execute()
        >>> print(results[url]["page"]["domain"])
        example.com
    """

    def __init__(self, parsers={}, supportedType={"url"}):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "UrlScan: Get full results"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("API_KEY", "")
        self.headers = {"accept": "application/json", "API-Key": API_KEY}

    def execute(self):
        """Execute result fetching on all parsed URLScan result URLs.

        Fetches full scan data from each valid result URL.

        Returns:
            dict[str, dict]: Keys are result URLs, values are complete scan
                result JSON or error dicts.
        """
        self.results = {}
        try:
            result_urls = self.get_observables().get("url", [])
            for url in result_urls:
                if url.startswith("https://urlscan.io/api/v1/result/"):
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[url] = response.json()
                    except Exception as e:
                        self.results = {"error": str(e)}
        except:
            pass
        return self.results

    def __str__(self):
        """Return human-readable representation of scan results.

        Calls :meth:`execute` and formats output as JSON array.

        Returns:
            str: JSON array of all scan results.
        """
        self.execute()
        return json.dumps([response for response in self.results.values()])


if __name__ == "__main__":
    from userTypeParser.domainParser import domainParser

    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain": parser}, ["domain"]))
    b = str(QueryUrlScanAction())
    print(b, parser.objects)

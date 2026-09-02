try:
    from userAction.actionInterface import actionInterface
except ImportError:
    from actionInterface import actionInterface

import json

import requests

BASE_API_URL = "https://api.urlquery.net/public/v1"
SEARCH_ENDPOINT = "/search/reports/"


class _UrlQueryMixin:
    def _get_api_key(self):
        api_key = self.conf.get("api_key", "")
        if not api_key:
            raise RuntimeError(
                "Missing URLQuery API key. Configure URLQUERY_API-KEY in .env"
            )
        return api_key

    def _build_headers(self):
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "X-APIKEY": self._get_api_key(),
        }

    def _normalize_int(self, value, default=20, minimum=0):
        try:
            normalized = int(str(value).strip())
            return max(minimum, normalized)
        except Exception:
            return default

    def _split_query_inputs(self, query):
        return [line.strip() for line in str(query or "").splitlines() if line.strip()]

    def _request_json(self, path, params=None):
        response = requests.get(
            f"{BASE_API_URL}{path}",
            headers=self._build_headers(),
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _extract_report_ids(self, search_json):
        report_ids = []
        for report in search_json.get("reports", []):
            report_id = report.get("report_id") or report.get("id")
            if report_id:
                report_ids.append(str(report_id))

        seen = set()
        unique_report_ids = []
        for report_id in report_ids:
            if report_id not in seen:
                seen.add(report_id)
                unique_report_ids.append(report_id)
        return unique_report_ids

    def _fetch_report(self, report_id):
        return self._request_json(f"/report/{report_id}")


class SearchInUrlQueryAction(_UrlQueryMixin, actionInterface):
    """An action module to search IoCs on URLQuery."""

    def __init__(self, parsers={}, supportedType={"ip", "domain", "url"}):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "UrlQuery: Search IoC"
        self.indicators = "🔑"
        self.load_conf("UrlQuery")

    def execute(self):
        self.results = {}
        self.observables = self.get_observables()

        observables = []
        for parser_type in self.supportedType:
            observables.extend(self.observables.get(parser_type, []))

        for observable in sorted(set(observables)):
            try:
                self.results[observable] = self._request_json(
                    SEARCH_ENDPOINT,
                    params={"query": observable, "limit": 20, "offset": 0},
                )
            except Exception as exc:
                self.results[observable] = {"error": str(exc)}

        return self.results

    def __str__(self) -> str:
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "longtext", "value": ""},
    "Max results": {"type": "text", "value": "20"},
    "Report mode": {"type": "bool", "value": False},
}


class QueryUrlQueryAction(_UrlQueryMixin, actionInterface):
    """An action module to run URLQuery searches."""

    def __init__(
        self, parsers={}, supportedType={"text"}, complex_param=DEFAULT_QUERY_PARAMETERS
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "UrlQuery: Query"
        self.indicators = "🔑"
        self.load_conf("UrlQuery")

    def _execute_single_query(self, query, limit, report_mode):
        search_json = self._request_json(
            SEARCH_ENDPOINT,
            params={"query": query, "limit": limit, "offset": 0},
        )
        if not report_mode:
            return search_json

        results = []
        for report_id in self._extract_report_ids(search_json)[:limit]:
            try:
                results.append(
                    {"reportId": report_id, "report": self._fetch_report(report_id)}
                )
            except Exception as exc:
                results.append({"reportId": report_id, "error": str(exc)})
        return results

    def execute(self) -> dict | list[dict]:
        try:
            queries = self._split_query_inputs(self.get_param_value("Query"))
            if not queries:
                self.results = {"error": "No query provided"}
                return self.results

            limit = self._normalize_int(
                self.get_param_value("Max results"),
                default=20,
                minimum=1,
            )
            report_mode = bool(self.get_param_value("Report mode"))

            if len(queries) == 1:
                self.results = self._execute_single_query(
                    queries[0], limit, report_mode
                )
                return self.results

            self.results = {}
            for query in queries:
                try:
                    self.results[query] = self._execute_single_query(
                        query, limit, report_mode
                    )
                except Exception as exc:
                    self.results[query] = {"error": str(exc)}
            return self.results
        except Exception as exc:
            self.results = {"error": str(exc)}
            return self.results

    def __str__(self) -> str:
        self.execute()
        return json.dumps(self.results)


if __name__ == "__main__":
    from userTypeParser.domainParser import domainParser

    parser = domainParser("example.com")
    print(str(SearchInUrlQueryAction({"domain": parser})))

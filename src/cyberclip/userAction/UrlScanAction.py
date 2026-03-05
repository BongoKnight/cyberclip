try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import urllib.parse
import requests
import json
import urllib
import time

BASE_SEARCH_URL = "https://urlscan.io/api/v1/search/"

class SearchInUrlScanAction(actionInterface):
    """An action module to search IP and domains on URLScan.  
    """

    def __init__(self, parsers = {}, supportedType = {"ip","domain","analytics"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "UrlScan: Search IoC"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("api-key","")
        self.headers = {"accept": "application/json", "API-Key": API_KEY}

        
    def execute(self) -> object:
        self.results = {}
        observables = []
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            try:
                query_url = BASE_SEARCH_URL + f"?q={observable}&size=20" 
                response = requests.get(query_url, headers=self.headers)
                self.results.update({observable:response.json()})
            except Exception as e:
                self.results.update({observable:str(e)})
        return self.results


    def __str__(self):
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


'''DEFAULT_QUERY_PARAMETERS = {"Query":{"type":"text","value":"*"}, "Max results":{"type":"text","value":"20"}}


class QueryUrlScanAction(actionInterface):
    """An action module to query URLScan through its API.

    Some queries might require an API Key.

    UrlScan:
    - api_key: <VT API Key> 
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param=DEFAULT_QUERY_PARAMETERS):
        super().__init__(parsers=parsers, supportedType=supportedType, complex_param=complex_param)
        self.description = "UrlScan: Query"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("api-key","")
        self.headers = {"accept": "application/json", "API-Key": API_KEY}

        
    def execute(self):
        self.results = {}
        try:
            query = self.get_param_value("Query")
            limit = int(self.get_param_value("Max results")) if  str(self.get_param_value("Max results")).isdecimal() else 20
            query_url = BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}&size={limit}" 
            response = requests.get(query_url, headers=self.headers)
            self.results = response.json()
        except Exception as e:
            self.results = {"error":str(e)}
        return self.results


    def __str__(self):
        self.execute()
        return json.dumps(self.results)'''

DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "text", "value": "*"},
    "Max results": {"type": "text", "value": "20"},
    "Fetch full results": {"type": "bool", "value": False},
    "Fetch DOM": {"type": "bool", "value": False},
    "Return summary": {"type": "bool", "value": True},
}

class QueryUrlScanAction(actionInterface):
    """Query urlscan.io Search API and optionally fetch full results (and DOM).

    Params:
    - Query: urlscan search query (ex: "*", "domain:example.com", "ip:1.2.3.4")
    - Max results: number of search hits to retrieve
    - Fetch full results: follow each hit's result and fetch full JSON
    - Fetch DOM: also fetch DOM snapshot (requires full results)
    - Return summary: return a compact summary instead of full raw JSON

    API key:
    Put it in Cyberclip config under section "UrlScan" with key "api-key".
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param=DEFAULT_QUERY_PARAMETERS):
        super().__init__(parsers=parsers, supportedType=supportedType, complex_param=complex_param)
        self.description = "UrlScan: Query"
        self.indicators = "🔑"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("api-key","")
        self.headers = {"accept": "application/json"}
        if API_KEY:
            self.headers["API-Key"] = API_KEY

    def _safe_int(self, value, default=20):
        try:
            return int(value)
        except:
            return default

    def _extract_hits(self, search_json):
        # urlscan search typically returns {"results":[...], "total":..., ...}
        hits = search_json.get("results", []) if isinstance(search_json, dict) else []
        return hits if isinstance(hits, list) else []

    def _hit_summary(self, hit):
        # Common fields seen in urlscan search results.
        # We keep it defensive because fields vary.
        task = hit.get("task", {}) if isinstance(hit, dict) else {}
        page = hit.get("page", {}) if isinstance(hit, dict) else {}

        return {
            "uuid": hit.get("_id") or hit.get("uuid") or hit.get("task", {}).get("uuid"),
            "url": task.get("url") or page.get("url"),
            "domain": page.get("domain") or task.get("domain"),
            "ip": page.get("ip"),
            "time": hit.get("sort") or hit.get("date") or hit.get("task", {}).get("time"),
            "result": hit.get("result"),  # sometimes present as URL
        }

    def _fetch_json(self, url):
        r = requests.get(url, headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def execute(self):
        self.results = {}
        try:
            query = self.get_param_value("Query")
            limit = self._safe_int(self.get_param_value("Max results"), default=20)

            fetch_full = bool(self.get_param_value("Fetch full results"))
            fetch_dom = bool(self.get_param_value("Fetch DOM"))
            summary_only = bool(self.get_param_value("Return summary"))

            query_url = BASE_SEARCH_URL + f"?q={urllib.parse.quote(str(query))}&size={limit}"
            search_json = self._fetch_json(query_url)

            hits = self._extract_hits(search_json)

            # Base output: search results (raw or summary)
            if summary_only:
                base = [self._hit_summary(h) for h in hits]
            else:
                base = hits

            output = {
                "query": query,
                "size": limit,
                "total": search_json.get("total"),
                "results": base,
            }

            # Optional: fetch full results
            if fetch_full:
                full_results = []
                dom_results = {}

                for h in hits:
                    result_url = h.get("result")
                    uuid = h.get("_id") or h.get("uuid") or h.get("task", {}).get("uuid")

                    # If result_url is present, it's the easiest: fetch it directly
                    if result_url:
                        try:
                            full_json = self._fetch_json(result_url)
                            full_results.append(full_json)

                            # Optional DOM fetch (only if we can derive a DOM URL)
                            if fetch_dom and uuid:
                                # urlscan provides DOM snapshot endpoint (varies by plan/paths).
                                # Common pattern in tooling is /dom/{uuid}/
                                dom_url = f"https://urlscan.io/dom/{uuid}/"
                                try:
                                    dom_r = requests.get(dom_url, headers=self.headers, timeout=15)
                                    if dom_r.status_code == 200:
                                        dom_results[uuid] = dom_r.text
                                except:
                                    pass

                        except Exception as e:
                            full_results.append({"error": str(e), "result": result_url, "uuid": uuid})
                        continue

                    # If no result_url, try Result API with uuid (if present)
                    if uuid:
                        try:
                            full_json = self._fetch_json(f"https://urlscan.io/api/v1/result/{uuid}/")
                            full_results.append(full_json)

                            if fetch_dom:
                                dom_url = f"https://urlscan.io/dom/{uuid}/"
                                try:
                                    dom_r = requests.get(dom_url, headers=self.headers, timeout=15)
                                    if dom_r.status_code == 200:
                                        dom_results[uuid] = dom_r.text
                                except:
                                    pass

                        except Exception as e:
                            full_results.append({"error": str(e), "uuid": uuid})

                output["full_results"] = full_results
                if fetch_dom:
                    output["dom"] = dom_results

            self.results = output

        except Exception as e:
            self.results = {"error": str(e)}

        return self.results

    def __str__(self):
        self.execute()
        return json.dumps(self.results, ensure_ascii=False)


if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain":parser},["domain"]))
    b = str(QueryUrlScanAction())
    print(b, parser.objects)
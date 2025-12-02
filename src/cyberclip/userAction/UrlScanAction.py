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
    """A action module to search IP and domains on URLScan.  
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


DEFAULT_QUERY_PARAMETERS = {"Query":{"type":"text","value":"*"}, "Max results":{"type":"text","value":"20"}}

class QueryUrlScanAction(actionInterface):
    """A action module to query URLScan through its API.

    Some querries might require an API Key.

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
        return "\r\n".join(json.dumps(value) for value in self.results.values())


if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain":parser},["domain"]))
    b = str(QueryUrlScanAction())
    print(b, parser.objects)
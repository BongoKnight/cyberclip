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
    """A action module to search IP and domains on URLScan.  
    """

    def __init__(self, parsers = {}, supportedType = {"ip","domain","analytics"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "UrlScan: Search"

        
    def execute(self) -> object:
        self.results = {}
        observables = []
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            try:
                query_url = BASE_SEARCH_URL + f"?q={observable}" 
                response = requests.get(query_url)
                self.results.update({observable:response.json()})
            except Exception as e:
                self.results.update({observable:str(e)})
        return self.results


    def __str__(self):
        self.execute()
        return "\n".join([f"{observable}\t{value}" for observable, value in self.results.items()])


DEFAULT_QUERY_PARAMETERS = {"Query":{"type":"text","value":"*"}}

class QueryUrlScanAction(actionInterface):
    """A action module to query URLScan through its API.

    Some querries might require an API Key.

    UrlScan:
    - api_key: <VT API Key> 
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param=DEFAULT_QUERY_PARAMETERS):
        super().__init__(parsers=parsers, supportedType=supportedType, complex_param=complex_param)
        self.description = "UrlScan: Query"
        self.load_conf("UrlScan")
        API_KEY = self.conf.get("api-key","")
        self.headers = {"accept": "application/json", "API-Key": API_KEY}

        
    def execute(self) -> object:
        self.results = {}
        try:
            query = self.get_param_value("Query")
            query_url = BASE_SEARCH_URL + f"?q={urllib.parse.quote(query)}" 
            response = requests.get(query_url, headers=self.headers)
            self.results = response.json()
        except Exception as e:
            self.results = {"error":str(e)}
        return self.results


    def __str__(self):
        return json.dumps(self.execute())


if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain":parser},["domain"]))
    print(a, parser.objects)
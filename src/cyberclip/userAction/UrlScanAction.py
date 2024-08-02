try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import requests

BASE_SEARCH_URL = "https://urlscan.io/api/v1/search/"

class SearchInUrlScanAction(actionInterface):
    """A action module to search IP and domains on URLScan.  
    """

    def __init__(self, parsers = {}, supportedType = {"ip","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Search on UrlScan"

        
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

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "urlscan.io"
    parser = domainParser(data)
    a = str(SearchInUrlScanAction({"domain":parser},["domain"]))
    print(a, parser.objects)
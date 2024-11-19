try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import time
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
from pathlib import Path

class baseDomainAction(actionInterface):
    """A action module, to return the base domain of a domain or URL.  
    For example : 

    - `https://www.example.com/path/of/page` returns `example.com`
    - `www.example.com` returns `example.com`
    """
    def __init__(self, parsers = {}, supportedType = {"url","domain"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "To base domain"
        self.results = {}
        
    def execute(self) -> object:
        self.results = {}
        self.observables = self.get_observables()
        if self.observables.get("url"):
            self.results.update({url:f"{'.'.join(urlparse(url).netloc.split('.')[-2:])}" for url in self.observables.get("url")})
        if self.observables.get("domain"):
            self.results.update({domain:f"{'.'.join(domain.split('.')[-2:])}" for domain in self.observables.get("domain")})
        return self.results

    
    def __str__(self):
        self.execute()
        return  "\n".join([value for key, value in self.results.items() if value!=""])


class inTop1MAction(actionInterface):
    """Return a list of domain in or out of the top 1M domains. The data are recovered from Cloudflare list.
    """
    def __init__(self, parsers = {}, supportedType = {"domain"}, complex_param={"Get domain NOT IN top 1M":{"type":"bool","value":True}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Top 1M domain"
        self.results = []

    def execute(self) -> object:
        self.results = []
        self.observables = self.get_observables()
        file_name = Path(__file__).parent / "../data/top1m.csv"
        if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
            try:
                url = "https://radar.cloudflare.com/charts/LargerTopDomainsTable/attachment?id=1545&top=1000000&startDate=2024-11-11&endDate=2024-11-18"
                response = requests.get(url, stream=True)
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(response.raw,f)
                del response
            except Exception as e:
                print("Error while retriving database from CloudFlare", e)
        TOP1M = []
        with open(file_name, "r") as f:
            TOP1M = set(f.read().splitlines()[1:])
        if self.get_param_value("Get domain NOT IN top 1M"):
            self.results = list(set(self.observables.get("domain")).difference(TOP1M))
        else:
            self.results = list(set(self.observables.get("domain")).intersection(TOP1M))
        return self.results

    def __str__(self):
        self.execute()
        return  "\n".join(self.results)
    

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbwww.todazdazdzto.com\ngoogle.com"
    domain_parser = domainParser(data)
    a = str(baseDomainAction({"domain":domain_parser}))
    b = str(inTop1MAction({"domain":domain_parser}))
    print(b)


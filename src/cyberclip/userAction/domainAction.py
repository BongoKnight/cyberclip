try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import time
import json
import requests
import tldextract
import pandas as pd
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class baseDomainAction(actionInterface):
    """Return the base domain of a domain or URL.  
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
            self.results.update({url:f"{tldextract.extract(url).registered_domain}" for url in self.observables.get("url")})
        if self.observables.get("domain"):
            self.results.update({domain:f"{tldextract.extract(domain).registered_domain}" for domain in self.observables.get("domain")})
        return self.results

    
    def __str__(self):
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append(f"{value}")
        return  "\n".join(lines)
    

class TldDomainAction(actionInterface):
    """Return the TLD of a domain or URL.  
For example : 

- `https://www.example.co.uk/path/of/page` returns `co.uk`
- `www.example.com` returns `com`
    """
    def __init__(self, parsers = {}, supportedType = {"url","domain"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Extract TLD"
        self.results = {}
        
    def execute(self) -> object:
        self.results = {}
        self.observables = self.get_observables()
        if self.observables.get("url"):
            self.results.update({url:f"{tldextract.extract(url).suffix}" for url in self.observables.get("url")})
        if self.observables.get("domain"):
            self.results.update({domain:f"{tldextract.extract(domain).suffix}" for domain in self.observables.get("domain")})
        return self.results

    
    def __str__(self):
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append(f"{key}\t{value}")
        return  "\n".join(lines)


class inTop1MAction(actionInterface):
    """Return a list of domain in or out (default) of the top 1M domains. The data are recovered from Cloudflare list.
    """
    def __init__(self, parsers = {}, supportedType = {"domain"}, complex_param={"Get domain NOT IN top 1M":{"type":"bool","value":True}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Domain: Top 1M"
        self.indicators = "📑"
        self.results = []

    def execute(self) -> object:
        self.results = []
        self.observables = self.get_observables()
        file_name = Path(__file__).parent / "../data/top1m.csv"
        if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
            try:
                url = f"https://downloads.majestic.com/majestic_million.csv"
                response = requests.get(url)
                with open(file_name, 'wb+') as f:
                    f.write(response.content)
                del response
            except Exception as e:
                print("Error while retriving database from Majestic Million", e)
        TOP1M = []
        with open(file_name, "r", encoding="utf-8") as f:
            TOP1M = set(pd.read_csv(file_name)["Domain"])
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


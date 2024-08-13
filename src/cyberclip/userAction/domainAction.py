try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
from urllib.parse import urlparse

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

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbwww.toto.com\na"
    text_parser = domainParser(data)
    a = str(baseDomainAction({"domain":text_parser}))
    print(a)
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import urllib

class baseUrlAction(actionInterface):
    """
    A action module, to return a link from a domain or an URL to the base dir.
    For example :
        - https://www.example.com/path/of/page returns https://www.example.com/
        - www.example.com returns https://www.example.com/
    """
    def __init__(self, parsers = {}, supportedType = {"url","domain","ip"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To base URL"
        self.base_url = {}
        
    def execute(self) -> object:
        """Execute the action."""
        self.base_url = {}
        self.observables = self.get_observables()
        if self.observables.get("url"):
            self.base_url.update({url:f"https://{urllib.parse.urlparse(url).netloc}" for url in self.observables.get("url")})
        if self.observables.get("domain"):
            self.base_url.update({domain:f"https://{domain}" for domain in self.observables.get("domain")})
        if self.observables.get("ip"):
            self.base_url.update({ip:f"https://{ip}" for ip in self.observables.get("ip")})
        return self.base_url

    
    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        return  "\n".join([value for key, value in self.base_url.items() if value!=""])

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(baseUrlAction({"domain":text_parser}))
    print(a)
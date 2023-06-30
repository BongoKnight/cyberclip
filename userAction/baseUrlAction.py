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
    def __init__(self, parsers = {}, supportedType = {"url","domain","ip"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "To base URL"
        self.results = {} 
        self.base_url = {}
        self.param = param_data
        
    def execute(self) -> object:
        """Execute the action."""
        self.base_url = {}
        self.results = {}
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("url"):
            self.base_url.update({url:f"https://{urllib.parse.urlparse(url).netloc}" for url in self.results.get("url")})
        if self.results.get("domain"):
            self.base_url.update({domain:f"https://{domain}" for domain in self.results.get("domain")})
        if self.results.get("ip"):
            self.base_url.update({ip:f"https://{ip}" for ip in self.results.get("ip")})
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
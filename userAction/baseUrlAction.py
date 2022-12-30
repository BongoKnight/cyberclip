try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import urllib

"""
A action module, to return a link from a domain or an URL to the base dir.
For example :
    - https://www.example.com/path/of/page returns https://www.example.com/
    - www.example.com returns https://www.example.com/
"""

class baseUrlAction(actionInterface):    
    def __init__(self, parsers = {}, supportedType = {"url","domain"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "To base URL"
        self.results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("url"):
            lines+= [f"https://{urllib.parse.urlparse(url).netloc}" for url in self.results.get("domain")]
        if self.results.get("domain"):
            lines+= [f"https://{domain}" for domain in self.results.get("domain")]
        lines.sort()
        return "\n".join([i for i in lines if i!=""])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(baseUrlAction({"domain":text_parser}))
    print(a)
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os

"""A action module, to open SARA item contained in the keyboard."""

class URLOpenAction(actionInterface):
    """Parser Interface defines the minimum functions a parser needs to implement."""
    
    def __init__(self, parsers ={}, supportedType = ["url"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Open URL in browser."
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("url"):
            for url in set(self.results.get("url")):
                lines.append(f"Openning {url}")
                os.startfile(f"{url}")
        return "\n".join([i for i in lines])
    
    def __str__(self):
        """Visual representation of the action"""
        return self.execute()


if __name__=='__main__':
    from userTypeParser.URLParser import URLParser

    data = "127.0.0.1, https://google.com/ SARA-574332 simon@vade.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    url_parser = URLParser(data)
    a = str(URLOpenAction({"url":url_parser},["url"]))
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os

"""A action module, to open transform lines to SQL IN querrie"""

class sortAction(actionInterface):    
    def __init__(self, parsers = {}, supportedType = ["text"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "To SQL search"
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = list(set(self.results.get("text")[0].splitlines()))
            lines.sort()
            return '"' + '","'.join(lines) +'"'

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(regexOrAction({'text':text_parser},["text"]))
    print(a)
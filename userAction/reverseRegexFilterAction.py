try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import re
"""
A action module to filter lines that don't match regex
"""


class reverseRegexFilterAction(actionInterface):    
    def __init__(self, parsers = {}, supportedType = {"text"}, param_data=""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Reverse filter with Regex"
        self.results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = self.results.get("text")[0].splitlines()
            return "\n".join([i for i in lines if not re.search(self.param, i)])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(reverseRegexFilterAction({"text":text_parser},["text"],param_data="^a"))
    print(a)
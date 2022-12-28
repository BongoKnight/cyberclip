try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os

"""A action module, to sort and deduplicates lines contained in the keyboard."""

class sortDedupAction(actionInterface):    
    def __init__(self, parsers = {}, supportedType = ["text"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Sort and deduplicate lines."
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = list(set(self.results.get("text")[0].splitlines()))
            lines.sort()
            return "\n".join([i for i in lines if i!=""])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortDedupAction({"text":text_parser},["text"]))
    print(a)
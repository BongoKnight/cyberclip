try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os

"""A action module, to open SARA item contained in the keyboard."""

class SARAOpenAction(actionInterface):
    """Parser Interface defines the minimum functions a parser needs to implement."""
    
    def __init__(self, parsers ={}, supportedType = ["sara"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Open all SARA events."
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        for sara in self.results.get("sara"):
            print(f"Openning {sara}")
            os.startfile(f"https://sara.internal.vadesecure.com/event/{sara}")
        return
    
    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        return "\n".join([f"{i} opened." for i in self.results.get("sara")])

if __name__=='__main__':
    from userTypeParser.SARAParser import SARAParser

    data = "127.0.0.1, 124.0.12.23 SARA-574332 simon@vade.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    sara_parser = SARAParser(data)
    a = str(SARAOpenAction({"sara":sara_parser},["sara"]))
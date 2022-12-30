try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import re



class toplLinesAction(actionInterface):
    """
    A action module to crop data to only the N first lines.
    """
    def __init__(self, parsers = {}, supportedType = {"text"}, param_data="10"):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Top N lines."
        self.results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """
        Return the N first lines of a text.
        
        Returns:
            lines[0:n] (list(str)): The n first lines
        """
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = self.results.get("text")[0].splitlines()
            return "\n".join([i for i in lines[:min(int(self.param), len(lines))]])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(toplLinesAction({"text":text_parser},["text"]))
    print(a)
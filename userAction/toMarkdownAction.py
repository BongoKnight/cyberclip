try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import re



class toMarkdownAction(actionInterface):   
    """
    A action module, to crop data to only the N first lines.
    """ 
    def __init__(self, parsers = {}, supportedType = {"tsv"}, param_data=""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "TSV to Md."
        self.results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        if self.parsers.get("tsv"):
            return self.parsers.get("tsv").objects.to_markdown(index=False)
        else:
            return ""


    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TSVParser import tsvParser
    data = "ip\tinfo\n127.0.0.1\tlocal"
    text_parser = tsvParser(data)
    a = str(toMarkdownAction({"tsv":text_parser},["tsv"]))
    print(a)
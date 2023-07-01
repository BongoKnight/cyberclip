try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import re



class toMarkdownAction(actionInterface):   
    """
    A action module, to transform a TSV data to a Markdown table.
    """ 
    def __init__(self, parsers = {}, supportedType = {"tsv"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "TSV to Md."
        
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
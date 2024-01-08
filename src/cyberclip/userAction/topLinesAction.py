try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import re



class toplLinesAction(actionInterface):
    """A action module to crop data to only the N first lines. Default 10 lines."""
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Number of lines":{"type":"text","value":"10"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Top N lines."
        
    def execute(self) -> object:
        """Return the N first lines of a text.
        
        Returns:
            lines[0:n] (list(str)): The n first lines
        """
        nb = self.get_param_value("Number of lines")
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            return "\n".join([i for i in lines[:min(int(nb), len(lines))]])

    
    def __str__(self):
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(toplLinesAction({"text":text_parser},["text"], {"Number of lines":{"type":"text","value":"1"}}))
    print(a)
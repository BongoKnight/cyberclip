try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import re



class toplLinesAction(actionInterface):
    """
    A action module to crop data to only the N first lines. Default 10 lines.
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, param_data="10"):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "Top N lines."
        
    def execute(self) -> object:
        """
        Return the N first lines of a text.
        
        Returns:
            lines[0:n] (list(str)): The n first lines
        """
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
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
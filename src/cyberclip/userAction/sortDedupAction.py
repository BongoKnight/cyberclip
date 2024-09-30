try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class sortDedupAction(actionInterface):
    """A action module, to sort and deduplicates lines contained in the keyboard."""

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Deduplicate and sort lines."

    def execute(self) -> object:
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = list(set(self.observables.get("text")[0].splitlines()))
            lines.sort()
            return "\n".join([i for i in lines if i!=""])
        return ""
    
    def __str__(self):
        return  self.execute()


class sortAction(actionInterface):    
    """A action module, to sort lines of a text.  
    Parameter can be passed over : 

    - if desc or reverse in param revert the order
    - if num, int, version in param sort by number
    """

    params = {"Numeric sort":{"type":"boolean","value":False} , "Reverse sort":{"type":"boolean","value":False}}

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param = params):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Sort lines."
        self.lines = []
        
    def execute(self) -> object:
        self.lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            self.lines = self.observables.get("text")[0].splitlines()
            self.lines.sort()
            if self.get_param_value("Numeric sort"):
                self.lines.sort(key=lambda s: int(re.search(r'^(\s*\d+)', s).group()) if re.search(r'^(\s*\d+)', s) else 0)       
            if self.get_param_value("Reverse sort"):
                self.lines.sort(reverse=True)
        
    def __str__(self):
        self.execute()
        return "\r\n".join(self.lines)
    
if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortDedupAction({"text":text_parser},["text"]))
    print(a)
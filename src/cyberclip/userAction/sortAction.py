try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import re


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
        
    def execute(self) -> object:
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            lines.sort()
            if self.get_param_value("Numeric sort"):
                lines.sort(key=lambda s: int(re.search(r'^(\s*\d+)', s).group()) if re.search(r'^(\s*\d+)', s) else 0)       
            if self.get_param_value("Reverse sort"):
                lines.sort(reverse=True)
            return "\n".join([i for i in lines])
        
    def __str__(self):
        return self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na\n2\n10"
    text_parser = TextParser(data)
    a = str(sortAction({"text":text_parser},["text"]))
    print(a)
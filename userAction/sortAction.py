try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import re


class sortAction(actionInterface):    
    """
    A action module, to sort lines of a text.
    Parameter can be passed over : 
        - if desc or reverse in param revert the order
        - if num, int, version in param sort by number
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, param_data: str =""):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Sort lines."
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            if set(["int","num","version"]) & set(self.param.split(",")):
                lines = sorted(lines, key=lambda s: int(re.search(r'^\d+', s).group()) if re.search(r'^\d+', s) else 0)       
            elif set(["desc","rev","reverse"]) & set(self.param.split(",")):
                lines.sort(reverse=True)
            else:
                lines.sort()
            return "\n".join([i for i in lines])

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortAction({"text":text_parser},["text"]))
    print(a)
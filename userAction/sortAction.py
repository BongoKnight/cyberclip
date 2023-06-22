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
        - if num in param sort by number
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Sort lines."
        self.results = {}
        self.param = ''
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = self.results.get("text")[0].splitlines()
            if set(["int","num","version"]) & set(self.param.split(",")):
                lines = sorted(lines, key=lambda s: int(re.search(r'^\d+', s).group()) if re.search(r'^\d+', s) else 0)       
            if set(["desc","rev","reverse"]) & set(self.param.split(",")):
                lines.sort(reverse=True)
            else:
                lines.sort()
            return "\n".join([i for i in lines])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortDedupAction({"text":text_parser},["text"]))
    print(a)
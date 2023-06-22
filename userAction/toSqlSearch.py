try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class toSqlSearch(actionInterface):    
    """A action module, to transform lines to an Python list or an IN SQL querry.
    For example if the text contain two lines with : a and b
    It will return "a","b".
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Python List/To SQL search"
        self.results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """Execute the action."""
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = list(set(self.results.get("text")[0].splitlines()))
            lines.sort()
            return '"' + '","'.join(lines) +'"'

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(toSqlSearch({'text':text_parser},["text"]))
    print(a)
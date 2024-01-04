try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class toSqlSearchAction(actionInterface):    
    """A action module, to transform lines to an Python list or an IN SQL querry.  
    For example if the text contain two lines with : a and b  
    It will return "a","b".  
    """

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To Python List or SQL search"

        
    def execute(self) -> object:
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = list(set(self.observables.get("text")[0].splitlines()))
            lines.sort()
            return '"' + '","'.join(lines) +'"'

    
    def __str__(self):
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(toSqlSearchAction({'text':text_parser},["text"]))
    print(a)
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class regexFilterAction(actionInterface):    
    """A action module to filter lines matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, param_data=""):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "Filter with Regex"
        
    def execute(self) -> object:
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            return "\n".join([i for i in lines if re.search(self.param, i)])

    
    def __str__(self):
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(regexFilterAction({"text":text_parser},["text"],param_data="^a"))
    print(a)
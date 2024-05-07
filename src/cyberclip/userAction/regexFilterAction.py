try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class regexFilterAction(actionInterface):    
    """A action module to filter lines matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Filter with Regex"
        
    def execute(self) -> object:
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
        return "\n".join([i for i in lines if re.search(self.get_param_value("Regex"), i)])

    
    def __str__(self):
        return  self.execute()

class reverseRegexFilterAction(actionInterface):    
    """A action module to filter lines not matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Reverse filter with Regex"
        
    def execute(self) -> object:
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
        return "\n".join([i for i in lines if not re.search(self.get_param_value("Regex"), i)])

    def __str__(self):
        return  self.execute()

class extractRegexGroupAction(actionInterface):    
    """A action module to extract group matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Extract group with Regex"
        
    def execute(self) -> object:
        text = ""
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0]
            matches = re.finditer(self.get_param_value("Regex"), text, re.MULTILINE)
            results = []
            for matchNum, match in enumerate(matches, start=1):
                results.append("\t".join(match.groups()))
            return "\n".join(results)
        else:
            return ""
        
    def __str__(self):
        return  self.execute()


if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "ba\nb\na"
    data2 = """aaa baba aa cba aba
    aaaa
"""
    text_parser = TextParser(data)
    text_parser2 = TextParser(data2)
    a = str(regexFilterAction({"text":text_parser},["text"],complex_param={"Regex":{"type":"text","value":"^a"}}))
    b = str(reverseRegexFilterAction({"text":text_parser},["text"],complex_param={"Regex":{"type":"text","value":"^a"}}))
    c = str(extractRegexGroupAction({"text":text_parser2},["text"],complex_param={"Regex":{"type":"text","value":"a{2,}"}}))
    d = str(extractRegexGroupAction({"text":text_parser2},["text"],complex_param={"Regex":{"type":"text","value":r"([a\s]ba)"}}))

    print(f"Match :\n{a}")
    print(f"Don't match :\n{b}")
    print(f"Extract :\n{c}")
    print(f"Extract multi group:\n{d}")
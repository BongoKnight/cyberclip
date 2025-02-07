try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class defangAction(actionInterface):    
    """Defang URLs, domains and IP addresses. Replace '.' by '[.]' and '^http' by 'hxxp'.
    """

    def __init__(self, parsers = {}, supportedType = {"ip","url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "IoC: Defang"
        
    def execute(self) -> list:
        observables = []
        results = []
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            defanged = observable.replace(".","[.]")
            defanged = re.sub("^http","hxxp", defanged)
            results.append(defanged)
        return results
    
    def __str__(self):
        return  "\r\n".join(self.execute())

class fangAction(actionInterface):    
    """Fang URLs, domains and IP addresses. Replace '[.]' by '.' and 'hxxp' by 'http'.  
    """

    def __init__(self, parsers = {}, supportedType = {"ip","url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "IoC: Fang"
        
    def execute(self) -> list:
        observables = []
        results = []
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            fanged = observable.replace("[.]",".")
            fanged = re.sub("(\[:/?/?\])","://", fanged)
            fanged = re.sub("^hxxp","http", fanged)
            results.append(fanged)
        return results
    
    def __str__(self):
        return  "\r\n".join(self.execute())

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\ngoogle.com\na"
    text_parser = domainParser(data)
    a = str(defangAction({'domain':text_parser},["domain"]))
    print(a)
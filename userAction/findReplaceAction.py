try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class findReplaceAction(actionInterface):    
    """
A action module to search and replace using regex.sub().
Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Search":"","Replace":""}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Find and replace"
        
    def execute(self) -> object:
        """Execute the action."""
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0]
            search_regex = self.complex_param.get('Search','')
            replace_regex = self.complex_param.get('Replace','')
            return re.sub(search_regex, replace_regex, text, flags= re.MULTILINE)

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\nabab"
    text_parser = TextParser(data)
    a = str(findReplaceAction({"text":text_parser},["text"],complex_param={"Search":r"^(a.*)$","Replace":r'\1\1'}))
    print(a)
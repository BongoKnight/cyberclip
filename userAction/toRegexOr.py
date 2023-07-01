try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class regexOrAction(actionInterface):    
    """A action module, to transform lines to an OR regex
    For example if the text contain two lines with : a and b
    It will return a|b.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, param_data: str =""):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "To Regex OR search"
        
    def execute(self) -> object:
        """Execute the action."""
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = list(set(self.observables.get("text")[0].splitlines()))
            lines.sort()
            lines = [i.replace(".","\\.") for i in lines]
            return '|'.join(lines)

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(regexOrAction({'text':text_parser},["text"]))
    print(a)
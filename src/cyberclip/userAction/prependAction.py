try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class prependAction(actionInterface):   
    """
    A action module, to prepend data to a given text.
    Usefull for adding header to data. Add the text to add as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Prepend text."

        
    def execute(self) -> object:
        """
        Add a line of text at the beginning of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            return self.param.replace("\\t","\t")+"\r\n"+self.observables.get("text")[0]
        return ""

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(prependAction([text_parser],["text"]))
    print(a)
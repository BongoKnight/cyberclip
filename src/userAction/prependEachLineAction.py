try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class prependEachLineAction(actionInterface):   
    """
    A action module, to prepend data to all the lines of a given text.
    Enter the text to preprend as a param.
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}, param_data: str =""):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "Prepend text on each line."
        
    def execute(self) -> object:
        """
        Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0].splitlines()
            return "\r\n".join([self.param.replace("\\t","\t") + line for line in text])

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(prependEachLineAction([text_parser],["text"]))
    print(a)
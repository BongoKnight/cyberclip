try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class prependAction(actionInterface):   
    """A action module, to prepend data to a given text.
    
    Usefull for adding header to data.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param = {"Text to add":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Prepend text."

        
    def execute(self) -> object:
        """Add a line of text at the beginning of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            return self.get_param_value("Text to add").replace("\\t","\t")+"\r\n"+self.observables.get("text")[0]
        return ""

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(prependAction({"text":text_parser},["text"], complex_param={"Text to add":{"type":"text","value":"c"}}))
    print(a)
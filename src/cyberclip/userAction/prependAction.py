try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface


class appendEachLineAction(actionInterface):   
    """A action module, to append data to each line of a given text.  
    Add the text to add as a param.
    """ 
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param: dict = {"Text to add":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Append text on each line."

    def execute(self) -> object:
        """Add a line of text at the beginning of each line of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0].splitlines()
            return "\r\n".join([line + self.get_param_value("Text to add").replace("\\t","\t") for line in text])

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

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


class prependEachLineAction(actionInterface):   
    """A action module, to prepend data to all the lines of a given text.
    Enter the text to preprend as a param.
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param: dict={"Text to prepend":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Prepend text on each line."
        
    def execute(self) -> object:
        """Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        text = self.observables.get("text","")[0].splitlines()
        return "\r\n".join([self.get_param_value("Text to prepend").replace("\\t","\t") + line for line in text])


    def __str__(self):
        return  self.execute()

class toLowerCaseAction(actionInterface):   
    """A action module, to lower case a text.
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To lower case"
        
    def execute(self) -> object:
        """Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text lower cased
        """
        self.observables = self.get_observables()
        text = self.observables.get("text","")[0].lower()
        return text

class toUperCaseAction(actionInterface):   
    """A action module, to UPPER case a text.
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To UPPER case"
        
    def execute(self) -> object:
        """Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text upper cased
        """
        self.observables = self.get_observables()
        text = self.observables.get("text","")[0].upper()
        return text

    def __str__(self):
        return  self.execute()


if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(prependAction({"text":text_parser},["text"], complex_param={"Text to add":{"type":"text","value":"c"}}))
    print(a)
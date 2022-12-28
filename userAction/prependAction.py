try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os



class prependAction(actionInterface):   
    """
    A action module, to prepend data to a given text.
    Usefull for adding header to data.
    """ 
    def __init__(self, parsers = {}, supportedType = ["text"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Prepend text."
        self.results = {}
        
    def execute(self) -> object:
        """
        Add a line of text at the beginning of a text.
        
        Return:
            text (str): Text with prepended data
        """
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            return self.param.replace("\\t","\t")+"\r\n"+self.results.get("text")[0]

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortAction([text_parser],["text"]))
    print(a)
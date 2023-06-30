try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os



class appendEachLineAction(actionInterface):   
    """
    A action module, to append data to each line of a given text.
    Add the text to add as a param.
    """ 
    def __init__(self, parsers = {}, supportedType = {"text"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Append text on each line."
        self.results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """
        Add a line of text at the beginning of each line of a text.
        
        Return:
            text (str): Text with prepended data
        """
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            text = self.results.get("text")[0].splitlines()
            return "\r\n".join([line + self.param.replace("\\t","\t") for line in text])

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(appendEachLineAction([text_parser],["text"]))
    print(a)
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class ExtractTextAction(actionInterface):
    """
    A action module to extract text from files contained in the clipboard.
    Make use of textract lib.
    """
    def __init__(self, parsers = {}, supportedType = {"filename"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Extract text from files."
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        import textract
        self.results = {}
        self.observables = self.get_observables()
        if filenames := self.observables.get("filename", []):
            for filename in filenames:
                try:
                    self.results.update({filename: textract.process(filename)})
                except Exception as e:
                    self.results.update({filename: f"Error while processing file : {str(e)}"})
    
    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        results = []
        for filename, text in self.results.items():
            if isinstance(text, bytes):
                results.append(str(text, "utf-8"))
            if isinstance(text, str):
                results.append(text)
        return  "\n\n".join(results)


if __name__=='__main__':
    from userTypeParser.filenameParser import filenameParser
    data = r'file'
    filename_parser = filenameParser(data)
    a = str(ExtractTextAction({"filename":filename_parser}))
    print(a)
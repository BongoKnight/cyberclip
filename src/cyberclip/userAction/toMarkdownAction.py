try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class toMarkdownAction(actionInterface):   
    """Transform a TSV data to a Markdown table.""" 
    def __init__(self, parsers = {}, supportedType = {"tsv"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "TSV to Md."
        
    def execute(self) -> object:
        lines = []
        if self.parsers.get("tsv"):
            return self.parsers.get("tsv").objects.to_markdown(index=False)
        else:
            return ""


    
    def __str__(self):
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TSVParser import tsvParser
    data = "ip\tinfo\n127.0.0.1\tlocal"
    text_parser = tsvParser(data)
    a = str(toMarkdownAction({"tsv":text_parser},["tsv"]))
    print(a)
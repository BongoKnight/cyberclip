try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class toMarkdownAction(actionInterface):   
    """Transform a CSV data to a Markdown table.""" 
    def __init__(self, parsers = {}, supportedType = {"csv"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "CSV to Md."
        
    def execute(self) -> object:
        lines = []
        if self.parsers.get("csv"):
            return self.parsers.get("csv").objects.to_markdown(index=False)
        else:
            return ""


    
    def __str__(self):
        return  self.execute()

if __name__=='__main__':
    from cyberclip.userTypeParser.CSVParser import csvParser
    data = "ip\tinfo\n127.0.0.1\tlocal"
    text_parser = csvParser(data)
    a = str(toMarkdownAction({"csv":text_parser},["csv"]))
    print(a)
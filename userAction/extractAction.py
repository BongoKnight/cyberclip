from userAction.actionInterface import actionInterface

"""A sample action module, that extract match from all parsers."""

class extractAction():
    """Extract all the instance for the given parsers."""
    
    def __init__(self, parsers = {}, supportedType = {"all","text"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description="Extract all elements."
        self.results = {}

    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        extracted_items = []
        for key, value in self.results.items():
            for i in value:
                extracted_items.append(i)
        return "\n".join(extracted_items)
        
    def execute(self) -> object:
        """Execute the action."""
        for parser_name, parser in self.parsers.items():
            if parser_name != "text":
                self.results.update({parser_name:parser.extract()})
        return self.results
    


if __name__=='__main__':
    from userTypeParser.IPParser import ipParser
    from userTypeParser.MD5Parser import md5Parser

    data = "127.0.0.1, 124.0.12.23 SARA-65890 simon@vade.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ip_parser = ipParser(data)
    md5_parser = md5Parser(data)
    a = str(extractAction([ip_parser, md5_parser],["ip"]))
    b = str(extractAction([ip_parser, md5_parser],["ip", "md5"]))
    print(a)
    print(b)
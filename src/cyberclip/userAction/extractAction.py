from userAction.actionInterface import actionInterface
"""A sample action module, that extract match from all parsers.
A list of exclusion can be passed, by default long observables as text, JSON, YAML and HTML are not returned.
"""

class extractAction(actionInterface):
    """Extract all the observables."""
    
    def __init__(self, parsers = {}, supportedType = {"all","text"}, exception = ["text","html", "json", "yaml"], complex_param={"Extract":{"type":"tags","value":["all"]}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description="Extract all elements."
        self.exception = exception


    def execute(self) -> object:
        for parser_name, parser in self.parsers.items():
            if parser_name not in self.exception:
                self.observables.update({parser_name:parser.extract()})
        return self.observables

    def __str__(self):
        self.execute()
        extracted_items = []
        extracted_type = self.get_param_value("Extract")
        if "all" in extracted_type:
            for key, value in self.observables.items():
                for i in value:
                    extracted_items.append(i)
        else:
            for key, value in self.observables.items():
                if key in extracted_type:
                    for i in value:
                        extracted_items.append(i)
        return "\n".join(extracted_items)
    


if __name__=='__main__':
    from userTypeParser.IPParser import ipParser
    from userTypeParser.MD5Parser import md5Parser

    data = "127.0.0.1, 124.0.12.23 user@domain.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ip_parser = ipParser(data)
    md5_parser = md5Parser(data)
    a = str(extractAction([ip_parser, md5_parser],["ip"]))
    b = str(extractAction([ip_parser, md5_parser],["ip", "md5"]))
    print(a)
    print(b)
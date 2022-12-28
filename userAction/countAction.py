try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

from collections import Counter

"""
A action module, to count lines contained in a text.

Return :
    <number_of_occurences>\t<occurence>
"""


class countAction(actionInterface):    
    def __init__(self, parsers = {}, supportedType = ["text"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Count lines occurences."
        self.results = {}
        self.param = ''
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("text"):
            lines = self.results.get("text")[0].splitlines()
            counts = Counter(lines)
            return "\n".join([f"{count}\t{line}" for line, count in counts.items()])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(countAction({"text":text_parser},["text"]))
    print(a)
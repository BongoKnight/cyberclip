try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

from collections import Counter

class countAction(actionInterface):    
    """
    A action module, to count lines contained in a text.

    Return :
        <number_of_occurences>\t<occurence>
    """
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Count lines occurences."
        
    def execute(self) -> object:
        """Count the number of occurence of each line."""
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            counts = Counter(lines)
            return counts

    
    def __str__(self):
        """Visual representation of the action"""
        counts = self.execute()
        return  "\n".join([f"{count}\t{line}" for line, count in counts.items()])

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(countAction({"text":text_parser},["text"]))
    print(a)
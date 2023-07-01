try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

class sortDedupAction(actionInterface):
    """A action module, to sort and deduplicates lines contained in the keyboard."""

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Deduplicate and sort lines."

    def execute(self) -> object:
        """Execute the action."""
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = list(set(self.observables.get("text")[0].splitlines()))
            lines.sort()
            return "\n".join([i for i in lines if i!=""])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortDedupAction({"text":text_parser},["text"]))
    print(a)
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class sortDedupAction(actionInterface):
    r"""Sort and deduplicate lines in text.

    Removes duplicate lines and sorts the remaining lines alphabetically.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("banana\napple\nbanana\ncherry\napple")
        >>> action = sortDedupAction({"text": parser})
        >>> print(action)
        apple
        banana
        cherry
    """

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Deduplicate and sort lines."

    def execute(self) -> object:
        """Execute sort and deduplication on text.

        Returns:
            str: Sorted, deduplicated lines (empty lines removed).
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = list(set(self.observables.get("text")[0].splitlines()))
            lines.sort()
            return "\n".join([i for i in lines if i!=""])
        return ""

    def __str__(self):
        """Return human-readable representation of sorted results.

        Returns:
            str: Formatted sorted and deduplicated text.
        """
        return  self.execute()


class sortAction(actionInterface):
    r"""Sort lines in text with configurable options.

    Sorts lines alphabetically or numerically, with optional reverse ordering.

    Supported Types:
        text

    Parameters:
        Numeric sort (bool): Sort by leading numbers instead of alphabetically.
            Default: False
        Reverse sort (bool): Reverse the sort order (Z-A or high-low).
            Default: False

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("10 items\n2 items\n100 items")
        >>> action = sortAction({"text": parser})
        >>> action.complex_param["Numeric sort"]["value"] = True
        >>> print(action)
        2 items
        10 items
        100 items
    """

    params = {"Numeric sort":{"type":"boolean","value":False} , "Reverse sort":{"type":"boolean","value":False}}

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param = params):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Sort lines."
        self.lines = []
        
    def execute(self) -> object:
        self.lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            self.lines = self.observables.get("text")[0].splitlines()
            self.lines.sort()
            if self.get_param_value("Numeric sort"):
                self.lines.sort(key=lambda s: int(re.search(r'^(\s*\d+)', s).group()) if re.search(r'^(\s*\d+)', s) else 0)       
            if self.get_param_value("Reverse sort"):
                self.lines.sort(reverse=True)
        
    def __str__(self):
        self.execute()
        return "\r\n".join(self.lines)
    
if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    text_parser = TextParser(data)
    a = str(sortDedupAction({"text":text_parser},["text"]))
    print(a)
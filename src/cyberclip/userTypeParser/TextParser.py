import re
from userTypeParser.ParserInterface import ParserInterface

class TextParser(ParserInterface):
    """Parse and extract any text from input.

    Universal parser that matches any non-empty string. Used for actions
    that should always be available regardless of content type.

    Regex Pattern:
        Not regex-based. Matches any non-empty text.

    Defanging Support:
        No. Matches text as-is.

    Example:
        >>> parser = TextParser("")
        >>> parser.contains()
        False
        >>> parser = TextParser("Any text content here")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['Any text content here']
    """

    def __init__(self, text, parsertype="text"):
        self.text = text
        self.parsertype = "text"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text is non-empty.

        Returns:
            bool: True if the text is not blank.
        """
        return bool(self.text)

    def extract(self) -> list[str]:
        """Extract the entire text.

        Returns:
            list[str]: A list containing the full text.
        """
        self.objects = [self.text]
        return self.objects
        
        
if __name__=="__main__":
    a = TextParser("1.3.4.5")
    b = TextParser("")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
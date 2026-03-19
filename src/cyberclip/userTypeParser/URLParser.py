import re
from userTypeParser.ParserInterface import ParserInterface


class URLParser(ParserInterface):
    r"""Parse and extract URLs from text.

    HTTP/HTTPS/FTP URLs with support for defanged notation.

    Regex Pattern:
        ``\b(?:(?:h(tt|xx)ps?|ftp|file)\[?:\/\/\]?|www\[?\.\]?|ftp\[?\.\]?)(?:([\-a-zA-Z0-9+&@#\/%=~_|$?!:,.\[\]\[\(\)]*)|[a-z\-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:([a-z\-A-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-zA-Z0-9\-+&@#\/%=~_|$])``

    Defanging Support:
        Yes. Handles ``hxxp`` (→ ``http``), ``[://]`` (→ ``://``), and ``[.]`` (→ ``.``).

    Example:
        >>> parser = URLParser("No URL here")
        >>> parser.contains()
        False
        >>> parser = URLParser("Visit http://example.com or hxxps://evil[.]com")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['http://example.com', 'hxxps://evil[.]com']
    """

    def __init__(self, text: str, parsertype="url"):
        self.text = text
        self.parsertype = "url"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one URL.

        Returns:
            bool: True if at least one URL is found in the text.
        """
        if re.search(r"\b(?:(?:h(tt|xx)ps?|ftp|file)\[?:\/\/\]?|www\[?\.\]?|ftp\[?\.\]?)(?:([\-a-zA-Z0-9+&@#\/%=~_|$?!:,.\[\]\[\(\)]*)|[a-z\-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:([a-z\-A-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-zA-Z0-9\-+&@#\/%=~_|$])",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all URL instances from the text.

        URLs are extracted in their original form (defanging is preserved in output).

        Returns:
            list[str]: A list of extracted URL values.
        """
        URLsIter = re.finditer(r"\b(?:(?:h(tt|xx)ps?|ftp|file)\[?:\/\/\]?|www\[?\.\]?|ftp\[?\.\]?)(?:([\-a-zA-Z0-9+&@#\/%=~_|$?!:,.\[\]\[\(\)]*)|[a-z\-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:([a-z\-A-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-zA-Z0-9\-+&@#\/%=~_|$])", self.text)
        URLs = [URL.group() for URL in URLsIter]
        self.objects = URLs
        return URLs
        
        
if __name__=="__main__":
    a = URLParser("dsfsd sdfsdf sdfsdhj j")
    b = URLParser("http://youpi.google.com/test.php?q=3Rte")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
import re
from userTypeParser.ParserInterface import ParserInterface


class B64Parser(ParserInterface):
    r"""Parse and extract Base64 strings from text.

    Base64 encoded strings that occupy entire lines (uses MULTILINE matching).

    Regex Pattern:
        ``^[A-Za-z0-9+/]+=*$`` (with MULTILINE flag)

    Defanging Support:
        No. Base64 strings are not typically defanged.

    Example:
        >>> parser = B64Parser("No base64 here")
        >>> parser.contains()
        False
        >>> parser = B64Parser("dG90bw==")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['dG90bw==']
    """

    def __init__(self, text: str, parsertype="b64"):
        self.text = text
        self.parsertype = "b64"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one Base64 line.

        Returns:
            bool: True if at least one valid Base64 line is found in the text.
        """
        b64strings = re.search(r"^[A-Za-z0-9+/]+=*$", self.text, re.MULTILINE)
        if b64strings and len(b64strings.group()) % 4 == 0:
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all Base64 line instances from the text.

        Only extracts strings with valid Base64 padding (length divisible by 4).

        Returns:
            list[str]: A list of extracted Base64 string values.
        """
        b64Iter = re.finditer(r"^[A-Za-z0-9+/]+=*$", self.text, re.MULTILINE)
        b64s = [b64.group() for b64 in b64Iter if len(b64.group()) % 4 == 0]
        self.objects = b64s
        return b64s
        
        
if __name__=="__main__":
    a = B64Parser("dqsdq. fdsf")
    b = B64Parser("dG90bw==")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
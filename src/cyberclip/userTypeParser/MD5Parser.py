import re
from userTypeParser.ParserInterface import ParserInterface


class md5Parser(ParserInterface):
    r"""Parse and extract MD5 hashes from text.

    MD5 hashes are 32-character hexadecimal strings.

    Regex Pattern:
        ``\b([0-9a-f]{32}|[0-9A-F]{32})\b``

    Defanging Support:
        No. Hashes are not typically defanged.

    Example:
        >>> parser = md5Parser("No hash here")
        >>> parser.contains()
        False
        >>> parser = md5Parser("Hash: 5d41402abc4b2a76b9719d911017c592")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['5d41402abc4b2a76b9719d911017c592']
    """

    def __init__(self, text: str, parsertype="md5"):
        self.text = text
        self.parsertype = "md5"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one MD5 hash.

        Returns:
            bool: True if at least one MD5 hash is found in the text.
        """
        if re.search(r"\b([0-9a-f]{32}|[0-9A-F]{32})\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all MD5 hash instances from the text.

        Returns:
            list[str]: A list of extracted MD5 hash values.
        """
        md5sIter = re.finditer(r"\b([0-9a-f]{32}|[0-9A-F]{32})\b", self.text)
        md5s = [md5.group(1) for md5 in md5sIter]
        self.objects = md5s
        return md5s
        
        
if __name__=="__main__":
    a = md5Parser("1.3.4.5")
    b = md5Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

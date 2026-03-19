import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

class SHA1Parser(ParserInterface):
    r"""Parse and extract SHA1 hashes from text.

    SHA1 hashes are 40-character hexadecimal strings.

    Regex Pattern:
        ``\b([0-9a-f]{40}|[0-9A-F]{40})\b``

    Defanging Support:
        No. Hashes are not typically defanged.

    Example:
        >>> parser = SHA1Parser("No hash here")
        >>> parser.contains()
        False
        >>> parser = SHA1Parser("Hash: aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d']
    """

    def __init__(self, text: str, parsertype="sha1"):
        self.text = text
        self.parsertype = "sha1"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one SHA1 hash.

        Returns:
            bool: True if at least one SHA1 hash is found in the text.
        """
        if re.search(r"\b([0-9a-f]{40}|[0-9A-F]{40})\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all SHA1 hash instances from the text.

        Returns:
            list[str]: A list of extracted SHA1 hash values.
        """
        SHA1sIter = re.finditer(r"\b([0-9a-f]{40}|[0-9A-F]{40})\b", self.text)
        SHA1s = [SHA1.group() for SHA1 in SHA1sIter]
        self.objects = SHA1s
        return SHA1s

class SHA256Parser(ParserInterface):
    r"""Parse and extract SHA256 hashes from text.

    SHA256 hashes are 64-character hexadecimal strings.

    Regex Pattern:
        ``\b([0-9a-f]{64}|[0-9A-F]{64})\b``

    Defanging Support:
        No. Hashes are not typically defanged.

    Example:
        >>> parser = SHA256Parser("No hash here")
        >>> parser.contains()
        False
        >>> parser = SHA256Parser("Hash: 2c26b46b68ffc68ff99b453c1d30413413422d706...")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['2c26b46b68ffc68ff99b453c1d30413413422d706...']
    """

    def __init__(self, text: str, parsertype="sha256"):
        self.text = text
        self.parsertype = "sha256"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one SHA256 hash.

        Returns:
            bool: True if at least one SHA256 hash is found in the text.
        """
        if re.search(r"\b([0-9a-f]{64}|[0-9A-F]{64})\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all SHA256 hash instances from the text.

        Returns:
            list[str]: A list of extracted SHA256 hash values.
        """
        SHA256sIter = re.finditer(r"\b([0-9a-f]{64}|[0-9A-F]{64})\b", self.text)
        SHA256s = [SHA256.group() for SHA256 in SHA256sIter]
        self.objects = SHA256s
        return SHA256s
        
if __name__=="__main__":
    a = SHA1Parser("ccdf ")
    b = SHA1Parser("AAAAAAAAAAAAAAAAAAAAAAAAAAA1AAAAAAAAAAAA ")
    c = SHA1Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    d = SHA1Parser("aaaaaaaaaaaaaAaaaaaaaaaaaaaaaaaaaaaaaaaa")

    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
    print(c.extract(), c.contains())
    print(d.extract(), d.contains())
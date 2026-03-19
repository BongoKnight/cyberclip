import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class CVEParser(ParserInterface):
    r"""Parse and extract CVE identifiers from text.

    CVE (Common Vulnerabilities and Exposures) identifiers in format CVE-YYYY-NNNNN.

    Regex Pattern:
        ``\bCVE-\d{4}-\d{3,5}\b`` (case-insensitive)

    Defanging Support:
        No. CVE identifiers are not typically defanged.

    Example:
        >>> parser = CVEParser("No CVE here")
        >>> parser.contains()
        False
        >>> parser = CVEParser("Vulnerabilities: CVE-2021-44228 and cve-2024-1234")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['CVE-2021-44228', 'cve-2024-1234']
    """

    def __init__(self, text: str, parsertype="cve"):
        self.text = text
        self.parsertype = "cve"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one CVE identifier.

        Returns:
            bool: True if at least one CVE identifier is found in the text.
        """
        if re.search(r"\bCVE-\d{4}-\d{3,5}\b",self.text, re.IGNORECASE) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all CVE identifier instances from the text.

        Returns:
            list[str]: A list of extracted CVE identifier values.
        """
        cveIter = re.finditer(r"\bCVE-\d{4}-\d{3,5}\b",self.text, re.IGNORECASE)
        cves = [cve.group() for cve in cveIter]
        self.objects = cves
        return cves
        
        
if __name__=="__main__":
    a = CVEParser("dsfsd sdfsdf sdfsdhj j")
    b = CVEParser("CVE-2024-22252")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
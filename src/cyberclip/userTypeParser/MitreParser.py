import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class MitreParser(ParserInterface):
    r"""Parse and extract MITRE ATT&CK TTP identifiers from text.

    MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)
    identifiers in format T#### or T####.### (e.g., T1566 or T1566.001).

    Regex Pattern:
        ``\bT\d{4}(\.\d{3})?\b``

    Defanging Support:
        No. TTP identifiers are not typically defanged.

    Example:
        >>> parser = MitreParser("No TTP here")
        >>> parser.contains()
        False
        >>> parser = MitreParser("Techniques: T1566.001 and T1059.005 detected")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['T1566.001', 'T1059.005']
    """

    def __init__(self, text: str, parsertype="mitre"):
        self.text = text
        self.parsertype = "mitre"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one MITRE ATT&CK TTP.

        Returns:
            bool: True if at least one TTP identifier is found in the text.
        """
        if re.search(r"\bT\d{4}(\.\d{3})?\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all MITRE ATT&CK TTP instances from the text.

        Returns:
            list[str]: A list of extracted TTP identifier values.
        """
        MitreIter = re.finditer(r"\bT\d{4}(\.\d{3})?\b", self.text)
        MitreTTPs = [TTP.group() for TTP in MitreIter]
        self.objects = MitreTTPs
        return MitreTTPs
        
        
if __name__=="__main__":
    a = MitreParser("dsfsd sdfsdf sdfsdhj j")
    b = MitreParser("T1012, T1016, T1027, T1033, T1059, T1059.001, T1059.005, T1082,T1083, T1087, T1095, T1112, T1140, T1547.001, T1547.009, T1560, T1566.001).")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
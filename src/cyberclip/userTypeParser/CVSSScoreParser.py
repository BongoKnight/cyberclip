import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class CVSSParser(ParserInterface):
    r"""Parse and extract CVSS vector strings from text.

    Supports:
        - CVSS v3.0 / v3.1
        - CVSS v4.0

    Regex Pattern:
        ``CVSS:(3\.[01]|4\.0)/...``

    Defanging Support:
        No.

    Example:
        >>> parser = CVSSParser("Score: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H']
    """

    # Matches both CVSS v3.x and v4.0 vectors
    CVSS_REGEX = re.compile(
        r"\bCVSS:(?:3\.[01]|4\.0)"
        r"(?:/[A-Z]{1,3}:[A-Z]{1,3})+\b",
        re.IGNORECASE,
    )

    def __init__(self, text: str, parsertype="cvss"):
        self.text = text
        self.parsertype = parsertype
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one CVSS vector.

        Returns:
            bool: True if at least one CVSS vector is found.
        """
        return bool(self.CVSS_REGEX.search(self.text))

    def extract(self) -> list[str]:
        """Extract all CVSS vectors from the text.

        Returns:
            list[str]: A list of extracted CVSS vectors.
        """
        vectors = [m.group() for m in self.CVSS_REGEX.finditer(self.text)]
        self.objects = vectors
        return vectors


if __name__ == "__main__":
    a = CVSSParser("No CVSS here.")
    b = CVSSParser(
        "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H "
        "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:P"
    )

    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
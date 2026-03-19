class ParserInterface():
    """Base interface for all CyberClip parsers.

    All parsers must inherit from this class and implement the :meth:`contains`
    and :meth:`extract` methods to detect and extract observables from text.

    Attributes:
        parsertype (str): Unique lowercase identifier for this parser type
            (e.g., "ip", "domain", "cve"). Used by actions in their
            ``supportedType`` set to declare compatibility.
        text (str): The input text to parse.
        objects (list): Extracted objects, populated by :meth:`extract`.

    Naming Convention:
        - Class names must contain "Parser" to be auto-discovered by CyberClip.
        - ``parsertype`` should be a short, descriptive lowercase string.

    Example:
        >>> from userTypeParser.ParserInterface import ParserInterface
        >>> class MyParser(ParserInterface):
        ...     def __init__(self, text):
        ...         super().__init__(text, parsertype="mytype")
        ...     def contains(self) -> bool:
        ...         return "match" in self.text
        ...     def extract(self) -> list:
        ...         self.objects = ["match"] if self.contains() else []
        ...         return self.objects
    """

    def __init__(self,text: str, parsertype = "interface"):
        self.parsertype = parsertype
        self.text = text
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one instance of the parsed type.

        Returns:
            bool: True if at least one match is found.
        """
        return False

    def extract(self) -> list:
        """Extract all instances of the parsed type from the text.

        Returns:
            list: A list of extracted objects.
        """
        return self.objects
    

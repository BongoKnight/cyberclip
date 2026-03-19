import yaml
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class YamlParser(ParserInterface):
    """Parse and extract YAML data from text.

    YAML data validated with yaml.safe_load(). Returns True if the parsed
    result is not a plain string.

    Regex Pattern:
        Not regex-based. Uses yaml.safe_load() for validation.

    Defanging Support:
        No. YAML data is not typically defanged.

    Example:
        >>> parser = YamlParser("Not YAML")
        >>> parser.contains()
        False
        >>> parser = YamlParser("key: value\\nlist:\\n  - item1\\n  - item2")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['key: value\\nlist:\\n- item1\\n- item2\\n']
    """

    def __init__(self, text: str, parsertype="yaml"):
        self.text = text
        self.parsertype = "yaml"

    def contains(self) -> bool:
        """Check whether the text contains valid YAML data.

        Returns:
            bool: True if valid YAML (non-string result) is found in the text.
        """
        try:
            if self.text:
                valid_yaml = yaml.safe_load(self.text)
                if not isinstance(valid_yaml, str):
                    return True
        except :
            return False
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all YAML data from the text.

        Returns:
            list[str]: A list containing YAML-encoded extracted data.
        """
        try:
            if self.text:
                self.objects = yaml.safe_load(self.text)
                if isinstance(self.objects, str):
                    self.objects = []
        except :
            self.objects = []
        return [yaml.dump(self.objects)]
        
        
if __name__=="__main__":
    a = YamlParser("""
- 'eric'
- 'justin'
- 'mary-kate'
    """)
    b = YamlParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
class ParserInterface():
    """Parser Interface defines the minimum functions a parser needs to implement."""
    
    def __init__(self,text: str, parsertype = "interface"):
        self.parsertype = parsertype
        self.text = text
        self.objects = []
        
    def contains(self) -> bool:
        """Have to return true if input text contains the parsed type."""
        return False
    
    def extract(self) -> list:
        """Extract a list of objects of parsed type."""
        return self.objects
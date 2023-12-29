"""Implementation of ParserInterface for Yaml strings.

Code exemple ::
    a = YamlParser("ccdf ")
    b = YamlParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import yaml
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class YamlParser(ParserInterface):
    """Parser for Yaml, use yaml.safe_load"""
    
    def __init__(self, text: str, parsertype="yaml"):
        self.text = text
        self.parsertype = "yaml"
        
    def contains(self):
        """Return true if text contains Yaml valid data"""
        try:
            if self.text:
                valid_yaml = yaml.safe_load(self.text)
                if not isinstance(valid_yaml, str):
                    return True
        except :
            return False
        else :
            return False
    
    def extract(self):
        """Return all JSON contained in text."""
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
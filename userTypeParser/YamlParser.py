"""Implementation of ParserInterface for Yaml strings.

Code exemple ::
    a = YamlParser("ccdf ")
    b = YamlParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import yaml
from userTypeParser.ParserInterface import ParserInterface


class YamlParser(ParserInterface):
    """Parser for Yaml, use yaml.safe_load"""
    
    def __init__(self, text: str, parsertype="yaml", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "yaml"
        self.log = logging.Logger("yaml")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains Yaml valid data"""
        try:
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
            self.objects = yaml.safe_load(self.text)
            if isinstance(self.objects, str):
                self.objects = []
        except :
            self.objects = []
        return [str(self.objects)]
        
        
if __name__=="__main__":
    a = YamlParser("""
- 'eric'
- 'justin'
- 'mary-kate'
    """)
    b = YamlParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
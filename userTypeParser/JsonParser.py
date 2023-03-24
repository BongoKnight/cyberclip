"""Implementation of ParserInterface for JSON strings.

Code exemple ::
    a = tsvParser("ccdf ")
    b = tsvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import json
from userTypeParser.ParserInterface import ParserInterface


class JSONParser(ParserInterface):
    """Parser for Json, use json.loads"""
    
    def __init__(self, text: str, parsertype="json", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "json"
        self.log = logging.Logger("json")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains JSON valid data"""
        try:
            valid_json = json.loads(self.text)
            if valid_json :
                return True
        except :
            return False
        else :
            return False
    
    def extract(self):
        """Return all JSON contained in text."""
        try:
            self.objects = json.loads(self.text)
        except :
            self.objects = []
        return [str(self.objects)]
        
        
if __name__=="__main__":
    a = JSONParser('{"a":"1"}')
    b = JSONParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
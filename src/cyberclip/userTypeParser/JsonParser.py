import json
from json.decoder import JSONDecodeError
import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class JSONParser(ParserInterface):
    """Implementation of ParserInterface for JSON strings.  
    Use json.loads

    Code exemple ::
        a = JsonParser("ccdf ")
        b = JsonParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    
    def __init__(self, text: str, parsertype="json"):
        self.text = text
        self.parsertype = "json"
        
    def contains(self):
        """Return true if text contains JSON valid data"""
        try:
            valid_json = json.loads(self.text)
            if valid_json :
                return True
        except :
            for match in re.findall(r'(\{.*\})', self.text):
                try:
                    json.loads(match[0])
                    return True
                except JSONDecodeError as e:
                    pass
            for line in self.text.splitlines():
                try:
                    json.loads(line)
                    return True
                except JSONDecodeError as e:
                    pass
            return False
        else :
            return False
    
    def extract(self):
        """Return all JSON contained in text."""
        self.objects = []
        try:
            self.objects = json.loads(self.text)
        except :
            for match in re.findall(r'(\{.*\})', self.text):
                try:
                    if json.loads(match[0]):
                        self.objects.append(json.loads(match[0]))
                except JSONDecodeError as e:
                    pass
            for line in self.text.splitlines():
                try:
                    if json_obj:=json.loads(line):
                        self.objects.append(json_obj)
                except JSONDecodeError as e:
                    pass
        return [json.dumps(self.objects)]
        
        
if __name__=="__main__":
    a = JSONParser('{"a":"1"}')
    b = JSONParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
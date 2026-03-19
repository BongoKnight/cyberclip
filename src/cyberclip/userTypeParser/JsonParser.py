import json
from json.decoder import JSONDecodeError
import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class JSONParser(ParserInterface):
    """Parse and extract JSON data from text.

    JSON data validated with json.loads(). Attempts to parse entire text,
    then falls back to extracting JSON objects or parsing line-by-line.

    Regex Pattern:
        Not fully regex-based. Uses json.loads() for validation.

    Defanging Support:
        No. JSON data is not typically defanged.

    Example:
        >>> parser = JSONParser("Not JSON")
        >>> parser.contains()
        False
        >>> parser = JSONParser('{"key": "value", "number": 42}')
        >>> parser.contains()
        True
        >>> parser.extract()
        ['{"key": "value", "number": 42}']
    """

    def __init__(self, text: str, parsertype="json"):
        self.text = text
        self.parsertype = "json"

    def contains(self) -> bool:
        """Check whether the text contains valid JSON data.

        Returns:
            bool: True if valid JSON is found in the text.
        """
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

    def extract(self) -> list[str]:
        """Extract all JSON data from the text.

        Returns:
            list[str]: A list containing JSON-encoded extracted data.
        """
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
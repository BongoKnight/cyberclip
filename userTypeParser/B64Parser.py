"""Implementation of ParserInterface for Base64 strings.

Code exemple ::
    a = asnumParser("dqsdq. fdsf")
    b = asnumParser("dG90bw==")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class B64Parser(ParserInterface):
    """
    Parser for base 64 text.
    """
    
    def __init__(self, text: str, parsertype="b64", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "b64"
        self.objects = []
        self.log = logging.Logger("b64")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """
        Return True if text contains at least one base 64 line.
        """
        b64strings = re.search(r"^[A-Za-z0-9+/]+=*$", self.text, re.MULTILINE)
        if b64strings and len(b64strings.group()) % 4 == 0:
            return True
        else :
            return False
    
    def extract(self):
        """
        Return all base64 lines contained in text.
        
        Return:
            b64 (list(str)): A list of as number with the following format : AS<Num> or as<num>
        """
        b64Iter = re.finditer(r"^[A-Za-z0-9+/]+=*$", self.text, re.MULTILINE)
        b64s = [b64.group() for b64 in b64Iter if len(b64.group()) % 4 == 0]
        self.objects = b64s
        self.log.debug(", ".join(self.objects))
        return b64s
        
        
if __name__=="__main__":
    a = B64Parser("dqsdq. fdsf")
    b = B64Parser("dG90bw==")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
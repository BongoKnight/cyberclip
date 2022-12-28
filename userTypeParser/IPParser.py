"""Implementation of ParserInterface for ip strings.

Code exemple ::
    a = ipParser("1212.1.2.3")
    b = ipParser("1.2.3[.]4")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class ipParser(ParserInterface):
    """Parser for ip."""
    
    
    def __init__(self, text: str, parsertype="ip", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "ip"
        self.objects = []
        self.log = logging.Logger("ip")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one ip."""
        if re.search(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all ip contained in text."""
        ipsIter = re.finditer(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\b", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        self.objects = ips
        self.log.debug(", ".join(self.objects))
        return ips
        
        
if __name__=="__main__":
    a = ipParser("1212.1.2.3")
    b = ipParser("1.2.3[.]4")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

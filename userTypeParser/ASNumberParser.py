"""Implementation of ParserInterface for asnum strings.

Code exemple ::
    a = asnumParser("dqsdq. fdsf")
    b = asnumParser("asnum.com")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class asnumParser(ParserInterface):
    """
    Parser for asnum.
    """
    
    
    def __init__(self, text: str, parsertype="asnum", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "asnum"
        self.objects = []
        self.log = logging.Logger("asnum")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """
        Return True if text contains at least one asnum.
        """
        if re.search(r"\bAS\d+\b", self.text, re.IGNORECASE) :
            return True
        else :
            return False
    
    def extract(self):
        """
        Return all asnum contained in text.
        
        Return:
            asmums (list(str)): A list of as number with the following format : AS<Num> or as<num>
        """
        asnumsIter = re.finditer(r"\bAS\d+\b", self.text, re.IGNORECASE)
        asnums = [asnum.group().replace("[.]",".") for asnum in asnumsIter]
        self.objects = asnums
        self.log.debug(", ".join(self.objects))
        return asnums
        
        
if __name__=="__main__":
    a = asnumParser("dqsdq. fdsf")
    b = asnumParser("AS2589")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
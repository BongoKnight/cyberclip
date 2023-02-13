"""Implementation of ParserInterface for HTML strings.

Code exemple ::
    a = URLParser("dsfsd sdfsdf sdfsdhj j")
    b = URLParser("Hello, <b>world</b>")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

Source : https://stackoverflow.com/questions/24856035/how-to-detect-with-python-if-the-string-contains-html-code
"""
import logging
import re
from bs4 import BeautifulSoup 
from userTypeParser.ParserInterface import ParserInterface


class HtmlParser(ParserInterface):
    """Parser for Mitre Att&ck TTP."""
    
    
    def __init__(self, text: str, parsertype="html", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "html"
        self.objects = []
        self.log = logging.Logger("HTML")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one Mitre TTP."""
        if bool(BeautifulSoup(self.text, "html.parser").find()) :
            return True
        else :
            return False
    
    def extract(self):
        """Return the whole text as object."""
        self.objects = [self.text]
        return self.objects
        
        
if __name__=="__main__":
    a = MitreParser("dsfsd sdfsdf sdfsdhj j")
    b = MitreParser("T1012, T1016, T1027, T1033, T1059, T1059.001, T1059.005, T1082,T1083, T1087, T1095, T1112, T1140, T1547.001, T1547.009, T1560, T1566.001).")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
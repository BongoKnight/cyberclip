"""Implementation of ParserInterface for mail strings.

Code exemple ::
    a = mailParser("1.3.4.5")
    b = mailParser("toto@domain.com")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class mailParser(ParserInterface):
    """Parser for mail."""

    def __init__(self, text: str, parsertype="mail", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "mail"
        self.objects = []
        self.log = logging.Logger("mail")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one mail."""
        if re.search(r"\b[^\s@=;]+@[^\s@,=]+\.[^\s@,=]+\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all mail contained in text."""
        mailsIter = re.finditer(r"\b[^\s@=;]+@[^\s@,=]+\.[^\s@,=]+\b", self.text)
        mails = [mail.group() for mail in mailsIter]
        self.objects = mails
        self.log.debug(", ".join(self.objects))
        return mails
        
        
if __name__=="__main__":
    a = mailParser("1.3.4.5")
    b = mailParser("toto@domain.com")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
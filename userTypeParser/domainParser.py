"""Implementation of ParserInterface for domain strings.

Code exemple ::
    a = domainParser("dqsdq. fdsf")
    b = domainParser("domain.com")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class domainParser(ParserInterface):
    """Parser for domain."""
    
    
    def __init__(self, text: str, parsertype="domain", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "domain"
        self.objects = []
        self.log = logging.Logger("domain")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one domain."""
        if re.search(r"\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b", self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all domain contained in text."""
        domainsIter = re.finditer(r"\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b", self.text)
        domains = [domain.group().replace(".]",".").replace("[.",".") for domain in domainsIter]
        self.objects = domains
        self.log.debug(", ".join(self.objects))
        return domains
        
        
if __name__=="__main__":
    a = domainParser("dqsdq. fdsf")
    b = domainParser("domain.com")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
"""Implementation of ParserInterface for ip strings.

Code exemple ::
    a = ipParser("1212.1.2.3")
    b = ipParser("1.2.3[.]4")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

class ipv4Parser(ParserInterface):
    """Parser for ipv4."""
    
    
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

class ipv6Parser(ParserInterface):
    """Parser for ipv6."""
    def __init__(self, text: str, parsertype="ipv6", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "ipv6"
        self.objects = []
        self.log = logging.Logger("ipv6")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one ip."""
        if re.search(r"([\s\r\n\t]|^)(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))([\s\r\n\t]|$)",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all ip contained in text."""
        ipsIter = re.finditer(r"([\s\r\n\t]|^)(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))([\s\r\n\t]|$)", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        self.objects = ips
        self.log.debug(", ".join(self.objects))
        return ips
        
if __name__=="__main__":
    a = ipv4Parser("1212.1.2.3")
    b = ipv4Parser("1.2.3[.]4")
    c = ipv6Parser("2001:41D0:1:2E4e::1")
    d = ipv6Parser("20001:41D0:1:2E4e::1")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
    print(c.extract(), c.contains())
    print(d.extract(), d.contains())

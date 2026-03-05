import re
import ipaddress
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

class ipv4Parser(ParserInterface):
    """Implementation of ParserInterface for ip strings.

    Code exemple ::
        a = ipParser("1212.1.2.3")
        b = ipParser("1.2.3[.]4")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    def __init__(self, text: str, parsertype="ip"):
        self.text = text
        self.parsertype = "ip"
        self.objects = []

        
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
        return ips


class CIDRParser(ParserInterface):
    """Parser for CIDR."""
    
    
    def __init__(self, text: str, parsertype="cidr"):
        self.text = text
        self.parsertype = "cidr"
        self.objects = []

        
    def contains(self):
        """Return true if text contains at least one CIDR"""
        if re.search(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\/\d{1,2}\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all CIDR contained in text."""
        ipsIter = re.finditer(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\/\d{1,2}\b", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        self.objects = ips
        return ips

# The old ipv6Parser, will delete later if not needed anymore
'''class ipv6Parser(ParserInterface):
    """Parser for ipv6."""
    def __init__(self, text: str, parsertype="ipv6"):
        self.text = text
        self.parsertype = "ipv6"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one ip."""
        if re.search(r"(\b|^)(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(\b|$)",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all ip contained in text."""
        ipsIter = re.finditer(r"(\b|^)(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(\b|$)", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        ips = [re.sub(r"([\s\r\n\t]|^|$)", r'', ip) for ip in ips]
        self.objects = ips
        return ips'''

class ipv6Parser(ParserInterface):
    """Parser for IPv6 addresses."""
    def __init__(self, text: str, parsertype="ipv6"):
        self.text = text
        self.parsertype = "ipv6"
        self.objects = []

    def contains(self):
        return len(self.extract()) > 0

    def extract(self):
        # 1) Find candidate tokens that contain ':' (IPv6-ish)
        # This grabs things like "2a0b:f4c2:2::33", possibly with punctuation around.
        candidates = re.findall(r"[0-9A-Fa-f:]{2,}", self.text)

        ips = []
        for cand in candidates:
            cand = cand.strip().strip("[](){}<>,;\"'")  # remove common surrounding punctuation
            if ":" not in cand:
                continue
            try:
                ip_obj = ipaddress.ip_address(cand)
                if isinstance(ip_obj, ipaddress.IPv6Address):
                    # normalize (compressed form)
                    ips.append(str(ip_obj))
            except ValueError:
                continue

        # optional: deduplicate while preserving order
        seen = set()
        unique = []
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                unique.append(ip)

        self.objects = unique
        return unique

        
if __name__=="__main__":
    a = ipv4Parser("1212.1.2.3")
    b = ipv4Parser("1.2.3[.]4")
    c = ipv6Parser("2001:41D0:1:2E4e::1")
    d = ipv6Parser("20001:41D0:1:2E4e::1")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
    print(c.extract(), c.contains())
    print(d.extract(), d.contains())

import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

class ipv4Parser(ParserInterface):
    r"""Parse and extract IPv4 addresses from text.

    IPv4 addresses in dotted decimal notation (e.g., 192.168.1.1).

    Regex Pattern:
        ``\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\b``

    Defanging Support:
        Yes. Converts ``[.]`` to ``.`` in extracted values.

    Example:
        >>> parser = ipv4Parser("No IP here")
        >>> parser.contains()
        False
        >>> parser = ipv4Parser("Server IP: 192.168.1.1 or 10[.]0[.]0[.]1")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['192.168.1.1', '10.0.0.1']
    """
    def __init__(self, text: str, parsertype="ip"):
        self.text = text
        self.parsertype = "ip"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one IPv4 address.

        Returns:
            bool: True if at least one IPv4 address is found in the text.
        """
        if re.search(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all IPv4 address instances from the text.

        Defanged notation (e.g., 192[.]168[.]1[.]1) is normalized to standard format.

        Returns:
            list[str]: A list of extracted IPv4 address values.
        """
        ipsIter = re.finditer(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\b", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        self.objects = ips
        return ips


class CIDRParser(ParserInterface):
    r"""Parse and extract CIDR notation from text.

    CIDR (Classless Inter-Domain Routing) notation for IP address ranges
    (e.g., 192.168.1.0/24).

    Regex Pattern:
        ``\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\/\d{1,2}\b``

    Defanging Support:
        Yes. Converts ``[.]`` to ``.`` in extracted values.

    Example:
        >>> parser = CIDRParser("No CIDR here")
        >>> parser.contains()
        False
        >>> parser = CIDRParser("Network: 10.0.0.0/8 and 192[.]168[.]0[.]0/16")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['10.0.0.0/8', '192.168.0.0/16']
    """

    def __init__(self, text: str, parsertype="cidr"):
        self.text = text
        self.parsertype = "cidr"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one CIDR notation.

        Returns:
            bool: True if at least one CIDR notation is found in the text.
        """
        if re.search(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\/\d{1,2}\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all CIDR notation instances from the text.

        Defanged notation (e.g., 192[.]168[.]0[.]0/16) is normalized to standard format.

        Returns:
            list[str]: A list of extracted CIDR notation values.
        """
        ipsIter = re.finditer(r"\b([0-9]{1,3}(\.|\[\.\])){3}[0-9]{1,3}\/\d{1,2}\b", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        self.objects = ips
        return ips

class ipv6Parser(ParserInterface):
    r"""Parse and extract IPv6 addresses from text.

    IPv6 addresses in standard and compressed notation (e.g., 2001:0db8::1).

    Regex Pattern:
        Complex pattern supporting full, compressed, and IPv4-embedded IPv6 formats.

    Defanging Support:
        Yes. Converts ``[.]`` to ``.`` in extracted values.

    Example:
        >>> parser = ipv6Parser("No IPv6 here")
        >>> parser.contains()
        False
        >>> parser = ipv6Parser("Server: 2001:0db8::1 or fe80::1")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['2001:0db8::1', 'fe80::1']
    """
    def __init__(self, text: str, parsertype="ipv6"):
        self.text = text
        self.parsertype = "ipv6"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one IPv6 address.

        Returns:
            bool: True if at least one IPv6 address is found in the text.
        """
        if re.search(r"(\b|^)(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(\b|$)",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all IPv6 address instances from the text.

        Defanged notation is normalized to standard format. Whitespace is stripped from matches.

        Returns:
            list[str]: A list of extracted IPv6 address values.
        """
        ipsIter = re.finditer(r"(\b|^)(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(\b|$)", self.text)
        ips = [ip.group().replace("[.]",".") for ip in ipsIter]
        ips = [re.sub(r"([\s\r\n\t]|^|$)", r'', ip) for ip in ips]
        self.objects = ips
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

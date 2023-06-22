try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import urllib
import socket
import dns
from dns import resolver

class DNSAction(actionInterface):
    """
    A action module, to return reverse DNS for an IP, and DNS for a domain.
    """
    def __init__(self, parsers = {}, supportedType = {"ip","domain"}, param_data: str ="A"):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "DNS/Reverse DNS"
        self.results = {}
        self.dns_results = {}
        self.param = param_data
        
    def execute(self) -> object:
        """A action module, to return reverse DNS for an IP, and DNS for a domain."""
        self.results = {}
        self.dns_results = {}
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("ip"):
            for ip in self.results.get("ip"):
                try:
                    self.dns_results.update({ip: ','.join(i[0] for i in [socket.getnameinfo((ip, 0), 0)])})
                except:
                    pass
        if self.results.get("domain"):
            for domain in self.results.get("domain"):
                try:
                    self.dns_results.update({domain:",".join([ip.to_text() for ip in resolver.resolve(domain, self.param)]) })
                except:
                    pass
        return self.dns_results
    
    def __str__(self):
        """Return result of DNS request for domain and of Reverse DNS for IP. For domain the type of NS reccord can be inputed as a parameter."""
        self.execute()
        return  "\n".join([f"{i}\t{self.dns_results.get(i)}" for i in self.dns_results if self.dns_results.get(i)!=""])

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(DNSAction({"domain":text_parser}))
    print(a)
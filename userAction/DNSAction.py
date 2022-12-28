try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import urllib
import socket
import dns
from dns import resolver

"""
A action module, to return reverse DNS for an IP, and DNS for a domain.
"""

class DNSAction(actionInterface):    
    def __init__(self, parsers = {}, supportedType = ["ip","domain"]):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "DNS/Reverse DNS"
        self.results = {}
        self.param = 'A'
        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        if self.results.get("ip"):
            lines+= [f"{ip}\t{','.join(i[0] for i in [socket.getnameinfo((ip, 0), 0)])}" for ip in self.results.get("ip")]
        if self.results.get("domain"):
            dns_results = {domain:",".join([ip.to_text() for ip in resolver.resolve(domain, self.param)]) for domain in self.results.get("domain")}
            lines+= [f"{domain}\t{dns_results.get(domain)}" for domain in self.results.get("domain")]
        lines.sort()
        return "\n".join([i for i in lines if i!=""])

    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(DNSAction({"domain":text_parser}))
    print(a)
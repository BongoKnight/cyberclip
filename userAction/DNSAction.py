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
    For a domain the a list of DNS reccord can be specified (default A) : ie. AAA,SPF,TXT.
    """
    def __init__(self, parsers = {}, supportedType = {"ipv6","ip","domain"}, param_data: str ="A"):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data= param_data)
        self.description = "DNS/Reverse DNS"
        self.dns_results = {}
        
    def execute(self) -> object:
        """A action module, to return reverse DNS for an IP, and DNS for a domain."""
        self.dns_results = {}
        self.observables = self.get_observables()
        if self.observables.get("ip"):
            for ip in self.observables.get("ip"):
                try:
                    self.dns_results.update({ip: ','.join(i[0] for i in [socket.getnameinfo((ip, 0), 0)])})
                except:
                    self.dns_results.update({ip:''})
        if self.observables.get("ipv6"):
            for ip in self.observables.get("ipv6"):
                try:
                    self.dns_results.update({ip: ','.join(i[0] for i in [socket.getnameinfo((ip, 0), 0)])})
                except:
                    self.dns_results.update({ip: ''})
        if self.observables.get("domain"):
            for domain in self.observables.get("domain"):
                dns_reccords = {}
                for type in self.param.split(","):
                    try:
                        dns_reccords.update({type:",".join([ip.to_text() for ip in resolver.resolve(domain, type)])})
                    except:
                        dns_reccords.update({type:"Error getting DNS reccord"})
                self.dns_results.update({domain:dns_reccords})
        return self.dns_results
    
    def __str__(self):
        """Return result of DNS request for domain and of Reverse DNS for IP. For domain the type of NS reccord can be inputed as a parameter."""
        self.execute()
        return  "\n".join([f"{i}\t{str(self.dns_results.get(i))}" for i in self.dns_results])

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(DNSAction({"domain":text_parser}))
    print(a)
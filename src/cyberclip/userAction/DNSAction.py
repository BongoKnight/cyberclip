try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import urllib
import socket
import dns
import json
from dns import resolver

class DNSAction(actionInterface):
    r"""Perform DNS lookups for domains and reverse DNS for IP addresses.

    Queries DNS records for domains and performs reverse DNS resolution for IPs.
    Supports multiple DNS record types with configurable query parameters.

    Supported Types:
        ip, ipv6, domain

    Network Activity:
        Makes DNS queries to configured DNS resolvers.

    Parameters:
        Records (tags): DNS record types to query for domains.
            Common values: A, AAAA, MX, TXT, SOA, NS, CNAME, SPF, DMARC
            Default: ["A", "TXT", "SOA", "NS", "MX"]

    Example:
        >>> from userTypeParser.domainParser import domainParser
        >>> parser = domainParser("example.com google.com")
        >>> action = DNSAction({"domain": parser})
        >>> results = action.execute()
        >>> print(action)
        example.com	{"A": "93.184.216.34", "TXT": "v=spf1..."}
        google.com	{"A": "142.250.185.46", "TXT": "..."}
    """
    CONF = {"Records":{"type":"tags","value":["A","TXT","SOA","NS","MX"]}}
    def __init__(self, parsers = {}, supportedType = {"ipv6","ip","domain"}, complex_param = CONF):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "DNS/Reverse DNS"
        self.dns_results = {}
        
    def execute(self) -> object:
        """Execute DNS lookups on all parsed observables.

        Performs reverse DNS lookups for IP addresses and forward DNS queries
        for domains with specified record types.

        Returns:
            dict[str, Any]: Keys are observables (IPs/domains), values are
                DNS results. For IPs: hostname string. For domains: dict of
                record types to values.
        """
        self.dns_results = {}
        self.observables = self.get_observables()
        if self.observables.get("ip"):
            for ip in self.observables.get("ip",[]):
                try:
                    self.dns_results.update({ip: ','.join(i[0] for i in [socket.getnameinfo((ip, 0), 0)])})
                except:
                    self.dns_results.update({ip:''})
        if self.observables.get("ipv6"):
            for ip in self.observables.get("ipv6",[]):
                try:
                    self.dns_results.update({ip: ','.join(i[0] for i in [socket.getnameinfo((ip, 0), 0)])})
                except:
                    self.dns_results.update({ip: ''})
        if domains := self.observables.get("domain",[]):
            for domain in domains:
                dns_records = {}
                for type in self.get_param_value("Records"):
                    try:
                        dns_records.update({type:",".join([ip.to_text() for ip in resolver.resolve(domain, type)])})
                    except:
                        dns_records.update({type:"Error getting DNS reccord"})
                self.dns_results.update({domain:dns_records})
        return self.dns_results
    
    def __str__(self):
        """Return human-readable representation of DNS results.

        Calls :meth:`execute` and formats output as TSV (tab-separated values).

        Returns:
            str: Formatted DNS results, one line per observable.
        """
        self.execute()
        results = []
        for key, value in self.dns_results.items():
            results.append(str(key) + "\t" + json.dumps(value))
        return  "\n".join(results)

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(DNSAction({"domain":text_parser}))
    print(a)
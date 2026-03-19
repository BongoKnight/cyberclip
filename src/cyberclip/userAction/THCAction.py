try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import requests

class SubdomainTHCDNSAction(actionInterface):
    r"""Retrieve known subdomains using The Hacker Choice (THC) DNS database.

    Queries the THC DNS database for historically observed subdomains of the
    specified domains. Results come from passive DNS collection.

    Supported Types:
        domain

    Network Activity:
        Makes requests to: ip.thc.org/api/v1/subdomains/download

    Parameters:
        Limit (text): Maximum number of subdomains to retrieve per domain.
            Default: 100

    Example:
        >>> from userTypeParser.domainParser import domainParser
        >>> parser = domainParser("example.com")
        >>> action = SubdomainTHCDNSAction({"domain": parser})
        >>> results = action.execute()
        >>> print(results["example.com"][:3])
        ['www.example.com', 'mail.example.com', 'ftp.example.com']

    Note:
        Service URL: https://ip.thc.org/
    """
    def __init__(self, parsers = {}, supportedType = {"domain"}, complex_param={"Limit":{"type":"text","value":"100"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Subdomains using THC.org"
        self.results = {}
        self.indicators = "🌍"
        
    def execute(self) -> dict:
        """Execute subdomain enumeration on all parsed domain observables.

        Queries THC DNS database for each domain and retrieves subdomain list.

        Returns:
            dict[str, list[str]]: Keys are domains, values are lists of
                subdomain strings.
        """
        self.url = "https://ip.thc.org/api/v1/subdomains/download"
        self.results = {}
        self.observables = self.get_observables()
        limit = self.get_param_value("Limit")
        if domains := self.observables.get("domain"):
            for domain in set(domains):
                THC_results = requests.get(self.url, 
                                        params={"domain":domain, "limit":limit, "hide_header":"true"}, 
                                        headers = {'Accept': 'text/csv'}
                                        )
                print(THC_results)
                if THC_results.status_code == 200 and THC_results.content:
                    self.results.update({domain:[line for line in THC_results.text.splitlines() if not line.startswith(";")]})
        return self.results

    
    def __str__(self):
        """Return human-readable representation of subdomain results.

        Calls :meth:`execute` and formats output as one subdomain per line.

        Returns:
            str: All discovered subdomains, one per line.
        """
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append("\r\n".join(value))
        return  "\n".join(lines)

class THCCNAMEAction(actionInterface):
    r"""Retrieve CNAME records using The Hacker Choice (THC) DNS database.

    Queries the THC DNS database for historically observed CNAME records
    pointing to the specified target domains.

    Supported Types:
        domain

    Network Activity:
        Makes requests to: ip.thc.org/api/v1/cnames/download

    Parameters:
        Limit (text): Maximum number of CNAME records to retrieve per domain.
            Default: 100

    Example:
        >>> from userTypeParser.domainParser import domainParser
        >>> parser = domainParser("example.com")
        >>> action = THCCNAMEAction({"domain": parser})
        >>> results = action.execute()
        >>> print(results["example.com"][:2])
        ['alias1.example.com,target1.example.com', 'alias2.example.com,target2.example.com']

    Note:
        Service URL: https://ip.thc.org/cn/
    """
    def __init__(self, parsers = {}, supportedType = {"domain"}, complex_param={"Limit":{"type":"text","value":"100"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "CNAME using THC.org"
        self.results = {}
        self.indicators = "🌍"
        
    def execute(self) -> dict:
        """Execute CNAME lookup on all parsed domain observables.

        Queries THC DNS database for each domain and retrieves CNAME records.

        Returns:
            dict[str, list[str]]: Keys are domains, values are lists of CNAME
                record strings.
        """
        self.url = "https://ip.thc.org/api/v1/cnames/download"
        self.results = {}
        self.observables = self.get_observables()
        limit = self.get_param_value("Limit")
        if domains := self.observables.get("domain"):
            for domain in set(domains):
                THC_results = requests.get(self.url, 
                                        params={"target_domain":domain, "limit":limit, "hide_header":"true"}, 
                                        headers = {'Accept': 'text/csv'}
                                        )
                if THC_results.status_code == 200 and THC_results.content:
                    self.results.update({domain:[line for line in THC_results.text.splitlines() if not line.startswith(";")]})
        return self.results

    
    def __str__(self):
        """Return human-readable representation of CNAME results.

        Calls :meth:`execute` and formats output as one CNAME per line.

        Returns:
            str: All discovered CNAME records, one per line.
        """
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append("\r\n".join(value))
        return  "\n".join(lines)

class THCReverseDNSAction(actionInterface):
    r"""Retrieve domains via reverse DNS using The Hacker Choice (THC) database.

    Queries the THC reverse DNS database for historically observed domains
    resolving to the specified IP addresses or CIDR ranges.

    Supported Types:
        ip, cidr

    Network Activity:
        Makes requests to: ip.thc.org/api/v1/download

    Parameters:
        Limit (text): Maximum number of domains to retrieve per IP/CIDR.
            Default: 100

    Example:
        >>> from userTypeParser.IPParser import ipv4Parser
        >>> parser = ipv4Parser("8.8.8.8")
        >>> action = THCReverseDNSAction({"ip": parser})
        >>> results = action.execute()
        >>> print(results["8.8.8.8"][:2])
        ['dns.google', 'google-public-dns-a.google.com']

    Note:
        Service URL: https://ip.thc.org/
    """
    def __init__(self, parsers = {}, supportedType = {"ip","cidr"}, complex_param={"Limit":{"type":"text","value":"100"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Reverse DNS using THC.org"
        self.results = {}
        self.indicators = "🌍"
        
    def execute(self) -> dict:
        """Execute reverse DNS lookup on all parsed IP/CIDR observables.

        Queries THC reverse DNS database for each IP or CIDR and retrieves
        associated domain names.

        Returns:
            dict[str, list[str]]: Keys are IPs/CIDRs, values are lists of
                domain strings.
        """
        self.url = "https://ip.thc.org/api/v1/download"
        self.results = {}
        self.observables = self.get_observables()
        limit = self.get_param_value("Limit")
        if ips := self.observables.get("ip"):
            for ip in set(ips):
                THC_results = requests.get(self.url, 
                                        params={"ip_address":ip, "limit":limit, "hide_header":"true"}, 
                                        headers = {'Accept': 'text/csv'}
                                        )
                if THC_results.status_code == 200 and THC_results.content:
                    self.results.update({ip:[line for line in THC_results.text.splitlines() if not line.startswith(";")]})
        if cidrs := self.observables.get("cidr"):
            for cidr in set(cidrs):
                THC_results = requests.get(self.url, 
                                        params={"ip_address":cidr, "limit":limit, "hide_header":"true"}, 
                                        headers = {'Accept': 'text/csv'}
                                        )
                if THC_results.status_code == 200 and THC_results.content:
                    self.results.update({cidr:[line for line in THC_results.text.splitlines() if not line.startswith(";")]})
        return self.results

    
    def __str__(self):
        """Return human-readable representation of reverse DNS results.

        Calls :meth:`execute` and formats output as one domain per line.

        Returns:
            str: All discovered domains, one per line.
        """
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append("\r\n".join(value))
        return  "\n".join(lines)

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbwww.toto.com\ngoogle.com"
    domain_parser = domainParser(data)
    a = str(THCCNAMEAction({"domain":domain_parser}))
    b = str(SubdomainTHCDNSAction({"domain":domain_parser}))
    print(b)


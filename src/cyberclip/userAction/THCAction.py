try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import requests

class SubdomainTHCDNSAction(actionInterface):
    """Retrieve subdomains using The Hacker Choice service.
    
    https://ip.thc.org/
    """
    def __init__(self, parsers = {}, supportedType = {"domain"}, complex_param={"Limit":{"type":"text","value":"100"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Subdomains using THC.org"
        self.results = {}
        self.indicators = "🌍"
        
    def execute(self) -> dict:
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
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append("\r\n".join(value))
        return  "\n".join(lines)
  
class THCCNAMEAction(actionInterface):
    """Retrieve CNAME using The Hacker Choice service.
    
    https://ip.thc.org/cn/
    """
    def __init__(self, parsers = {}, supportedType = {"domain"}, complex_param={"Limit":{"type":"text","value":"100"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "CNAME using THC.org"
        self.results = {}
        self.indicators = "🌍"
        
    def execute(self) -> dict:
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
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append("\r\n".join(value))
        return  "\n".join(lines)
    
class THCReverseDNSAction(actionInterface):
    """Retrieve domains using reverse DNS from The Hacker Choice service.
    
    https://ip.thc.org/cn/
    """
    def __init__(self, parsers = {}, supportedType = {"ip","cidr"}, complex_param={"Limit":{"type":"text","value":"100"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Reverse DNS using THC.org"
        self.results = {}
        self.indicators = "🌍"
        
    def execute(self) -> dict:
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


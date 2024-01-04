try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import ipaddress


def explode_to(network, prefixlen=24):
    if isinstance(network, str):
        network = ipaddress.ip_network(network)
    if network.prefixlen > prefixlen:
        return []
    if network.prefixlen == prefixlen:
        return [str(network)]
    subnets = [explode_to(sub, prefixlen) for sub in network.subnets()]
    return [str(nwk) for sublist in subnets for nwk in sublist]

class ToCIDR24Action(actionInterface):
    """A action module, to return a list of /24 CIDR from a bigger CIDR.
    """
    def __init__(self, parsers = {}, supportedType = {"cidr", "ip"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To CIDR/24"
        self.exploded_cidr = {}
        
    def execute(self) -> object:
        self.exploded_cidr = {}
        self.observables = self.get_observables()
        for cidr in self.observables.get("cidr", []):
            self.exploded_cidr.update({cidr:", ".join(explode_to(cidr))})
        for ip in self.observables.get("ip", []):
            network = ".".join(ip.split(".")[:-1]) + ".0/24"
            self.exploded_cidr.update({ip:network})
        return self.exploded_cidr
    
    def __str__(self):
        self.execute()
        return  "\n".join([f'{key}: {value}' for key, value in self.exploded_cidr.items() if value!=""])

if __name__=='__main__':
    from userTypeParser.IPParser import CIDRParser
    data = "5.253.84.0/22 5.253.86.0/24 45.129.230.0/23"
    text_parser = CIDRParser(data)
    a = str(ToCIDR24Action({"domain":text_parser}))
    print(a)
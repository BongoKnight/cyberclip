try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import requests
import json
from dataclasses import dataclass, fields


BASE_URL = "https://crt.sh/"

@dataclass
class Certificate:
    issuer_ca_id: int
    issuer_name: str
    common_name: str
    name_value: str
    id: int
    entry_timestamp: str
    not_before: str
    not_after: str
    serial_number: str
    result_count: int

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)


class crtshCertificatesAction(actionInterface):
    """Recover list of certificate for a domain.  
    """

    def __init__(self, parsers = {}, supportedType = {"domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Crt.sh: Get certificates"

        
    def execute(self) -> object:
        self.results = {}
        for domain in self.get_observables().get("domain", []):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                }
                response = requests.get(f"{BASE_URL}?output=json&q={domain}", headers=headers)
                self.results.update({domain:response.json()})
            except Exception as e:
                self.results.update({domain:str(e)})
        return self.results


    def __str__(self):
        self.execute()
        lines = []
        for domain, certificates in self.results.items():
            lines.append(f"{domain}\t{json.dumps(certificates, indent=None)}")
        return "\n".join(lines)

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "draw.io"
    domain_parser = domainParser(data)
    a = str(crtshCertificatesAction({"domain":domain_parser},["domain"]))
    print(a)
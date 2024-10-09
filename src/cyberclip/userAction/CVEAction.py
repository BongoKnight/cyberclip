try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import json
import requests

from dataclasses import dataclass

class CVEExplainerAction(actionInterface):
    """A action module, to get info on CVE number.
    """
    def __init__(self, parsers = {}, supportedType = {"cve"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "CVE: Explain number"
        self.decoded_b64 = []
        
    def execute(self) -> object:
        self.base_url = {}
        self.observables = self.get_observables()
        self.results = {}
        if cves:= self.observables.get("cve",[]):
            for cve in cves:
                url = "https://cveawg.mitre.org/api/cve/" + cve.upper()
                info = requests.get(url)
                if info.status_code == 200:
                    self.results[cve]=info.json()
                else:
                    self.results[cve]={}
        return self.results

    
    def __str__(self):
        self.execute()
        results = []
        for cve, value in self.results.items():
            if value :
                    cveitem = CVEItem(value)
                    results.append(f"{cve}\t{cveitem.score}\t{cveitem.severity}\t{cveitem.affected_product}\t{cveitem.published}\t{cveitem.description}\t{cveitem.references}")
            else:
                results.append(f"{cve}\t\t\t\t\t\t\t")
        return  "\n".join(results)

@dataclass
class CVEItem:
    data: dict
    
    @property
    def affected_product(self):
        affected_info = self.data.get("containers",{}).get("cna",{}).get("affected",[])
        return ",".join([i.get("product", "") for i in affected_info if i.get("product", "")])
    
    @property
    def published(self):
        return self.data.get("cveMetadata",{}).get("datePublished","")
    
    @property
    def references(self):
        return ",".join([i.get("url","") for i in self.data.get("containers",{}).get("cna",{}).get("references",[]) if i.get("url","")])

    @property
    def score(self):
        try:
            return str(self.data.get("containers",{}).get("cna",{}).get("metrics",{})[0].get("cvssV3_1", {}).get("baseScore",""))
        except:
            return "N/A"
        
    @property
    def severity(self):
        try:
            return self.data.get("containers",{}).get("cna",{}).get("metrics",{})[0].get("cvssV3_1", {}).get("baseSeverity","")
        except:
            return "N/A"

    @property
    def description(self):
        descs = self.data.get("containers",{}).get("cna",{}).get("descriptions",[])
        if descs :
            return descs[0].get("value","").replace("\n","").replace("\r","").replace("\t","")
        else:
            return ""

if __name__=='__main__':
    from userTypeParser.CVEParser import CVEParser
    cveitem = CVEItem({"dataType":"CVE_RECORD","dataVersion":"5.0","cveMetadata":{"cveId":"CVE-2024-22252","assignerOrgId":"dcf2e128-44bd-42ed-91e8-88f912c1401d","state":"PUBLISHED","assignerShortName":"vmware","dateReserved":"2024-01-08T18:43:15.942Z","datePublished":"2024-03-05T17:57:22.043Z","dateUpdated":"2024-03-05T17:57:22.043Z"},"containers":{"cna":{"affected":[{"defaultStatus":"unaffected","product":"VMware ESXi","vendor":"n/a","versions":[{"lessThan":"ESXi80U2sb-23305545","status":"affected","version":"8.0 ","versionType":"custom"},{"lessThan":"ESXi80U1d-23299997","status":"affected","version":"8.0","versionType":"custom"},{"lessThan":"ESXi70U3p-23307199","status":"affected","version":"7.0","versionType":"custom"}]},{"defaultStatus":"unaffected","product":"VMware Workstation","vendor":"n/a","versions":[{"lessThan":"17.5.1","status":"affected","version":"17.x","versionType":"custom"}]},{"defaultStatus":"unaffected","product":"VMware Fusion","vendor":"n/a","versions":[{"lessThan":"13.5.1","status":"affected","version":"13.x","versionType":"custom"}]},{"defaultStatus":"unaffected","product":"VMware Cloud Foundation","vendor":"n/a","versions":[{"status":"affected","version":"5.x"},{"status":"affected","version":"4.x"}]}],"datePublic":"2024-03-05T04:00:00.000Z","descriptions":[{"lang":"en","supportingMedia":[{"base64":False,"type":"text/html","value":"VMware ESXi, Workstation, and Fusion contain a use-after-free vulnerability in the XHCI USB controller.&nbsp;A malicious actor with local administrative privileges on a virtual machine may exploit this issue to execute code as the virtual machine's VMX process running on the host. On ESXi, the exploitation is contained within the VMX sandbox whereas, on Workstation and Fusion, this may lead to code execution on the machine where Workstation or Fusion is installed."}],"value":"VMware ESXi, Workstation, and Fusion contain a use-after-free vulnerability in the XHCI USB controller. A malicious actor with local administrative privileges on a virtual machine may exploit this issue to execute code as the virtual machine's VMX process running on the host. On ESXi, the exploitation is contained within the VMX sandbox whereas, on Workstation and Fusion, this may lead to code execution on the machine where Workstation or Fusion is installed."}],"metrics":[{"cvssV3_1":{"attackComplexity":"LOW","attackVector":"LOCAL","availabilityImpact":"HIGH","baseScore":9.3,"baseSeverity":"CRITICAL","confidentialityImpact":"HIGH","integrityImpact":"HIGH","privilegesRequired":"NONE","scope":"CHANGED","userInteraction":"NONE","vectorString":"CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H","version":"3.1"},"format":"CVSS","scenarios":[{"lang":"en","value":"GENERAL"}]}],"providerMetadata":{"orgId":"dcf2e128-44bd-42ed-91e8-88f912c1401d","shortName":"vmware","dateUpdated":"2024-03-05T17:57:22.043Z"},"references":[{"url":"https://www.vmware.com/security/advisories/VMSA-2024-0006.html"}],"source":{"discovery":"UNKNOWN"},"title":"Use-after-free vulnerability","x_generator":{"engine":"Vulnogram 0.1.0-dev"}}}})
    print(f"{cveitem.score}\t{cveitem.severity}\t{cveitem.affected_product}\t{cveitem.published}\t{cveitem.references}\t{cveitem.description}")

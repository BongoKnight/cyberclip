import pandas as pd
import shutil
import requests
import os
import sys
import ipaddress
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

AS_DB = pd.DataFrame()
file_name = os.path.join("as.gz")
try:
    url = "https://iptoasn.com/data/ip2asn-v4-u32.tsv.gz"
    response = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        shutil.copyfileobj(response.raw,f)
    del response
    AS_DB = pd.read_csv(file_name, header=None, sep="\t", compression="gzip")
    AS_DB.rename(columns={0:"min_ip",1:"max_ip",2:"as_num",3:"as_loc",4:"as_info"}, inplace=True)
except Exception as e:
    print("Error while retriving database from IpToASN")


class IpToAsAction(actionInterface):
    """
    A action module, to crop data to only the N first lines.
    """
    def __init__(self, parsers = {}, supportedType = ["ip"], param_data=""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "IP to AS Number"
        self.results = {}
        self.param = param_data

        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        if self.parsers.get("ip"):
            if len(AS_DB.columns):
                ips = self.parsers.get("ip").extract()
                for ip in ips:
                    int_ip = int(ipaddress.ip_address(ip))
                    response = AS_DB.loc[(AS_DB["min_ip"]<int_ip) & (AS_DB["max_ip"]>=int_ip)].to_dict(orient="row")
                    if len(response)>0:
                        infos = response[0]
                        infos.update({"min_ip": str(ipaddress.ip_address(infos.get("min_ip",0))),
                                "max_ip": str(ipaddress.ip_address(infos.get("max_ip",0))),
                                "as_num":"AS"+str(infos.get("as_num"))})
                        infos = [str(info) for key, info in infos.items()]
                        infos = '\t'.join(infos)
                        lines.append(f"{ip}\t{infos}")
                return "\n".join(lines)
            else:
                return "\n".join(self.parsers.get("ip").objects)
        else:
            return ""


    
    def __str__(self):
        """Visual representation of the action"""
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.IPParser import ipParser
    data = "ip\tinfo\n154.0.123.1\tlocal"
    text_parser = ipParser(data)
    a = str(IpToAsAction({"ip":text_parser},["ip"]))
    print(a, text_parser.objects)
import pandas as pd
import shutil
import requests
import asyncio
import os
import sys
import re
import ipaddress
import time
from pathlib import Path
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

AS_DB = None
AS_IPv6_DB = None
AS_RANGE = None

def get_AS_data():
    global AS_DB, AS_RANGE
    file_name = Path(__file__).parent / "../data/as.gz"
    if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
        print("Getting data...")
        try:
            url = "https://iptoasn.com/data/ip2asn-v4-u32.tsv.gz"
            response = requests.get(url, stream=True)
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(response.raw,f)
            del response
        except Exception as e:
            print("Error while retriving database from IpToASN")
    try: 
        if not AS_DB:
            AS_DB = pd.read_csv(file_name, header=None, sep="\t", compression="gzip")
            AS_DB.rename(columns={0:"min_ip",1:"max_ip",2:"as_num",3:"as_loc",4:"as_info"}, inplace=True)
            AS_DB["CIDRS"] = AS_DB.apply(lambda row: [i for i in ipaddress.summarize_address_range(
                ipaddress.ip_address(row["min_ip"]),
                ipaddress.ip_address(row["max_ip"]))], axis=1)
    except Exception as e:
        print("Error while loading AS database")
    return AS_DB

def get_IPv6_AS_data():
    global AS_IPv6_DB
    file_name = Path(__file__).parent / "../data/as_ipv6.gz"
    if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
        try:
            url = "https://iptoasn.com/data/ip2asn-v6.tsv.gz"
            response = requests.get(url, stream=True)
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(response.raw,f)
            del response
        except Exception as e:
            print("Error while retriving database from IpToASN")
    try: 
        if not AS_IPv6_DB:
            AS_IPv6_DB = pd.read_csv(file_name, header=None, sep="\t", compression="gzip")
            AS_IPv6_DB.rename(columns={0:"min_ip",1:"max_ip",2:"as_num",3:"as_loc",4:"as_info"}, inplace=True)
            AS_IPv6_DB["min_ip"] =  AS_IPv6_DB["min_ip"].apply(ipaddress.ip_address)
            AS_IPv6_DB["max_ip"] =  AS_IPv6_DB["max_ip"].apply(ipaddress.ip_address)
            AS_IPv6_DB["CIDRS"] = AS_IPv6_DB.apply(lambda row: [i for i in ipaddress.summarize_address_range(
                row["min_ip"],
                row["max_ip"])], axis=1)
    except Exception as e:
        print("Error while loading AS database")
    return AS_IPv6_DB


class AsToCidrAction(actionInterface):
    """Return a list of CIDR depending of an Autonomous System.
    
    `AS15169` returns `AS15169	8.8.4.0/24 8.8.8.0/24`
    """
    
    def __init__(self, parsers = {}, supportedType = {"asnum"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "AS Number to CIDR"

    def execute(self) -> object:
        self.results = {}
        get_AS_data()
        get_IPv6_AS_data()
        self.observables = self.get_observables()
        if self.observables.get("asnum", []):
            if len(AS_DB.columns):
                AS_numbers = self.observables.get("asnum", [])
                for as_num in AS_numbers:
                    int_as = int(re.search(r"\d+",as_num).group())
                    AS_RANGE = AS_DB.loc[AS_DB["as_num"]==int_as]
                    AS_RANGE = AS_RANGE[["as_num","CIDRS"]]
                    AS_RANGE = AS_RANGE.groupby('as_num').agg(sum).reset_index()
                    response = AS_RANGE.loc[AS_RANGE["as_num"]==int_as].to_dict(orient="records")
                    if len(response)>0:
                        infos = response[0]
                        self.results.update({as_num:infos})
                return self.results
            else:
                return self.observables.get("asnum", [])
        else:
            return []

    def __str__(self):
        self.execute()
        lines = []
        for asnum, infos in self.results.items():
            cidrs = infos.get("CIDRS",[])
            infos_str = " ".join([cidr.compressed for cidr in cidrs])
            lines.append(f"{asnum}\t{infos_str}")
        return "\n".join(lines)  


class AsInformationAction(actionInterface):
    """Return information about an Autonomous System.

    `AS15169` returns `AS15169	15169	GOOGLE	US	8.8.4.0/24 8.8.8.0/24 <list of GOOGLE CIDR>`
    """
    
    def __init__(self, parsers = {}, supportedType = {"asnum"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "AS Number information"

    def execute(self) -> object:
        self.results = {}
        get_AS_data()
        get_IPv6_AS_data()
        self.observables = self.get_observables()
        if self.observables.get("asnum", []):
            if len(AS_DB.columns):
                AS_numbers = self.observables.get("asnum", [])
                for as_num in AS_numbers:
                    int_as = int(re.search(r"\d+",as_num).group())
                    AS_RANGE = AS_DB.loc[AS_DB["as_num"]==int_as]
                    AS_RANGE = AS_RANGE[["as_num","as_info","as_loc","CIDRS"]]
                    AS_RANGE = AS_RANGE.groupby(['as_num','as_info','as_loc']).agg(sum).reset_index()
                    response = AS_RANGE.loc[AS_RANGE["as_num"]==int_as].to_dict(orient="records")
                    if len(response)>0:
                        infos = response[0]
                        self.results.update({as_num:infos})
                return self.results
            else:
                return self.observables.get("asnum", [])
        else:
            return []

    def __str__(self):
        self.execute()
        lines = []
        for asnum, infos in self.results.items():
            cidrs = infos.get("CIDRS",[])
            infos_cidr = " ".join([cidr.compressed for cidr in cidrs])
            nb_cidrs = len(cidrs)
            clean_infos = infos.copy()
            clean_infos.update({"CIDRS":infos_cidr,"Nb of CIDR":nb_cidrs})
            info = "\t".join([str(data) for data in clean_infos.values()])
            lines.append(f"{asnum}\t{info}")
        return "\n".join(lines)  


class IpToAsAction(actionInterface):
    """Return Autonomous System information refering to an IP address.

    `8.8.8.8` will return `8.8.8.8	8.8.8.0	8.8.8.255	AS15169	US	GOOGLE`
    """
    
    def __init__(self, parsers = {}, supportedType = {"ipv6","ip"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "IP to AS Number"

    def execute(self) -> object:
        self.results = {}
        get_AS_data()
        get_IPv6_AS_data()
        self.observables = self.get_observables()
        if self.observables.get("ip", []):
            if len(AS_DB.columns):
                ips = self.observables.get("ip", [])
                for ip in ips:
                    infos = {}
                    int_ip = int(ipaddress.ip_address(ip))
                    response = AS_DB.loc[(AS_DB["min_ip"]<int_ip) & (AS_DB["max_ip"]>=int_ip)].to_dict(orient="records")
                    if len(response)>0:
                        infos = response[0]
                        infos.update({"min_ip": str(ipaddress.ip_address(infos.get("min_ip",0))),
                                "max_ip": str(ipaddress.ip_address(infos.get("max_ip",0))),
                                "as_num":"AS" + str(infos.get("as_num"))})
                        self.results.update({ip:infos})
        if self.observables.get("ipv6", []):
            if len(AS_IPv6_DB.columns):
                ips = self.observables.get("ipv6", [])
                for ip in ips:
                    infos = {}
                    ip_object = ipaddress.ip_address(ip)
                    response = AS_IPv6_DB.loc[(AS_IPv6_DB["min_ip"]<ip_object) & (AS_IPv6_DB["max_ip"]>=ip_object)].to_dict(orient="records")
                    if len(response)>0:
                        infos = response[0]
                        infos.update({"min_ip": str(infos.get("min_ip",0)),
                                "max_ip": str(infos.get("max_ip",0)),
                                "as_num":"AS" + str(infos.get("as_num"))})
                        self.results.update({ip:infos})
        return self.results

    def __str__(self):
        self.execute()
        lines = []
        for ip, infos in self.results.items():
            infos_str = "\t".join([str(info) for key, info in infos.items() if key not in ["CIDRS"]])
            lines.append(f"{ip}\t{infos_str}")
        return "\n".join(lines)  


if __name__=='__main__':
    from userTypeParser.ASNumberParser import asnumParser
    data = "ip\tinfo\n154.0.123.1 as64286"
    text_parser = asnumParser(data)
    a = str(AsInformationAction({"asnum":text_parser},["asnum"]))
    print(a, text_parser.objects)

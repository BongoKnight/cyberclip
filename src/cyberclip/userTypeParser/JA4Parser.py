import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

class ja4Parser(ParserInterface):
    """Implementation of ParserInterface for JA4 hash.

    Code exemple ::
        a = ja4Parser("1.3.4.5")
        b = ja4Parser("ge11cn020000_9ed1ff1f7b03_cd8dafe26982")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    
    def __init__(self, text: str, parsertype="ja4"):
        self.text = text
        self.parsertype = "ja4"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one JA4."""
        if re.search(r"\b(JA4(H|X|SSH|S|T|TScan)?=?)?([a-z0-9]{4,20}_[a-z0-9]{4,20}(_[a-z0-9]{4,20})?|(\d+)_\d+-[\d\-_]+)\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all JA4 contained in text."""
        ja4sIter = re.finditer(r"\b(JA4(H|X|SSH|S|T|TScan)?=?)?([a-z0-9]{4,20}_[a-z0-9]{4,20}(_[a-z0-9]{4,20})?|(\d+)_\d+-[\d\-_]+)\b", self.text)
        ja4s = [ja4.group(3) for ja4 in ja4sIter if re.search("\d{2}", ja4.group(3))]
        self.objects = ja4s
        return ja4s
        
        
if __name__=="__main__":
    a = ja4Parser("1.3.4.5")
    b = ja4Parser("""JA4=t13d1516h2_8daaf6152771_02713d6af862	JA4=q13d0312h3_55b375c5d22e_06cda9e17597
        JA4H=ge11cn020000_9ed1ff1f7b03_cd8dafe26982	
        JA4=t13d201100_2b729b4bf6f3_9e7b989ebec8	JA4S=t120300_c030_5e2616a54c73
        JA4=t13d190900_9dc949149365_97f8aa674fd9	JA4S=t130200_1301_a56c5b993250
        JA4H=ge11cn060000_4e59edc1297a_4da5efaf0cbd	JA4X=2166164053c1_2166164053c1_30d204a01551
        JA4=t13d880900_fcb5b95cb75a_b0d3b4ac2a14	JA4S=t130200_1302_a56c5b993250
        JA4X=2bab15409345_af684594efb4_000000000000	
        JA4X=1a59268f55e5_1a59268f55e5_795797892f9c	
        JA4H=po10nn060000_cdb958d032b0	
        JA4H=po11nn050000_d253db9d024b	
        JA4=t13d191000_9dc949149365_e7c285222651	
        JA4SSH=c76s76_c71s59_c0s70	
        JA4T=64240_2-1-3-1-1-4_1460_8	
        JA4TScan=28960_2-4-8-1-3_1460_3_1-4-8-16	
    """)
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

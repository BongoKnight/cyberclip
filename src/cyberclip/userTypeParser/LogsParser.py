import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class CombinedLogParser(ParserInterface):
    """Implementation of ParserInterface for CombinedLog strings. Cf. https://httpd.apache.org/docs/2.4/fr/logs.html

    Code exemple ::
        a = CombinedLogParser('127.0.0.1 - jg [27/Apr/2012:11:27:36 +0700] "GET /regexcookbook.html HTTP/1.1" 200 2326')
        b = CombinedLogParser("CVE-2024-22252")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """

    REGEX = r"^(\S+) \S+ (\S+) \[([^\]]+)\] \"([A-Z]+) ([^ \"]+)? HTTP/[0-9.]+\" ([0-9]{3}) ([0-9]+|-) \"([^\"]*)\" \"([^\"]*)\"$"    
    
    def __init__(self, text: str, parsertype="cve"):
        self.text = text
        self.parsertype = "combinedlog"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one combined log formated line"""
        if re.search(CombinedLogParser.REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all Combined logs contained in text."""
        logIter = re.finditer(CombinedLogParser.REGEX ,self.text, re.IGNORECASE)
        logs = [log.group() for log in logIter]
        self.objects = logs
        return logs
        
class CommonLogParser(ParserInterface):
    """Implementation of ParserInterface for CommonLog strings. Cf. https://httpd.apache.org/docs/2.4/fr/logs.html

    Code exemple ::
        a = CommonLogParser('127.0.0.1 - jg [27/Apr/2012:11:27:36 +0700] "GET /regexcookbook.html HTTP/1.1" 200 2326')
        b = CommonLogParser("CVE-2024-22252")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """

    REGEX = r'^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? HTTP\/[0-9.]+" ([0-9]{3}) ([0-9]+|-)$'    
    
    def __init__(self, text: str, parsertype="cve"):
        self.text = text
        self.parsertype = "commonlog"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one CommonLog formated line"""
        if re.search(CommonLogParser.REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all common log contained in text."""
        logIter = re.finditer(CommonLogParser.REGEX ,self.text, re.IGNORECASE)
        logs = [log.group() for log in logIter]
        self.objects = logs
        return logs


if __name__=="__main__":
    a = CommonLogParser('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326')
    b = CommonLogParser("CVE-2024-22252")
    c = CombinedLogParser('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"')
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
    print(c.extract(), c.contains())
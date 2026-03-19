import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class CombinedLogParser(ParserInterface):
    r"""Parse and extract Apache Combined Log Format entries from text.

    Combined Log Format includes Common Log Format plus referer and user-agent.

    Regex Pattern:
        ``^(\S+) \S+ (\S+) \[([^\]]+)\] \"([A-Z]+) ([^ \"]+)? HTTP/[0-9.]+\" ([0-9]{3}) ([0-9]+|-) \"([^\"]*)\" \"([^\"]*)\"$``
        (case-insensitive)

    Defanging Support:
        No. Log entries are not typically defanged.

    Example:
        >>> parser = CombinedLogParser("Not a log")
        >>> parser.contains()
        False
        >>> parser = CombinedLogParser('127.0.0.1 - user [10/Oct/2000:13:55:36 -0700] "GET /page.html HTTP/1.0" 200 2326 "http://example.com" "Mozilla/5.0"')
        >>> parser.contains()
        True
        >>> parser.extract()
        ['127.0.0.1 - user [10/Oct/2000:13:55:36 -0700] "GET /page.html HTTP/1.0" 200 2326 "http://example.com" "Mozilla/5.0"']

    Reference:
        https://httpd.apache.org/docs/2.4/fr/logs.html
    """

    REGEX = r"^(\S+) \S+ (\S+) \[([^\]]+)\] \"([A-Z]+) ([^ \"]+)? HTTP/[0-9.]+\" ([0-9]{3}) ([0-9]+|-) \"([^\"]*)\" \"([^\"]*)\"$"

    def __init__(self, text: str, parsertype="combinedlog"):
        self.text = text
        self.parsertype = "combinedlog"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one Combined Log Format line.

        Returns:
            bool: True if at least one Combined Log Format entry is found.
        """
        if re.search(CombinedLogParser.REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all Combined Log Format entries from the text.

        Returns:
            list[str]: A list of extracted Combined Log Format log lines.
        """
        logIter = re.finditer(CombinedLogParser.REGEX ,self.text, re.IGNORECASE)
        logs = [log.group() for log in logIter]
        self.objects = logs
        return logs
        
class CommonLogParser(ParserInterface):
    r"""Parse and extract Apache Common Log Format entries from text.

    Common Log Format (CLF) for HTTP server access logs.

    Regex Pattern:
        ``^(\S+) \S+ (\S+) \[([^\]]+)\] \"([A-Z]+) ([^ \"]+)? HTTP\/[0-9.]+\" ([0-9]{3}) ([0-9]+|-)$``
        (case-insensitive)

    Defanging Support:
        No. Log entries are not typically defanged.

    Example:
        >>> parser = CommonLogParser("Not a log")
        >>> parser.contains()
        False
        >>> parser = CommonLogParser('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326')
        >>> parser.contains()
        True
        >>> parser.extract()
        ['127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326']

    Reference:
        https://httpd.apache.org/docs/2.4/fr/logs.html
    """

    REGEX = r'^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? HTTP\/[0-9.]+" ([0-9]{3}) ([0-9]+|-)$'

    def __init__(self, text: str, parsertype="commonlog"):
        self.text = text
        self.parsertype = "commonlog"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one Common Log Format line.

        Returns:
            bool: True if at least one Common Log Format entry is found.
        """
        if re.search(CommonLogParser.REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all Common Log Format entries from the text.

        Returns:
            list[str]: A list of extracted Common Log Format log lines.
        """
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
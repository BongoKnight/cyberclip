try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import re

class defangAction(actionInterface):
    r"""Defang URLs, domains, and IP addresses for safe display.

    Converts indicators of compromise (IoCs) to non-clickable/non-resolvable
    format by replacing dots with [.] and http with hxxp. Prevents accidental
    clicks on malicious URLs in reports.

    Supported Types:
        ip, url, domain

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> parser = URLParser("http://malicious.example.com/payload")
        >>> action = defangAction({"url": parser})
        >>> print(action)
        hxxp://malicious[.]example[.]com/payload

        >>> from userTypeParser.IPParser import ipv4Parser
        >>> parser = ipv4Parser("192.168.1.1")
        >>> action = defangAction({"ip": parser})
        >>> print(action)
        192[.]168[.]1[.]1
    """

    def __init__(self, parsers = {}, supportedType = {"ip","url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "IoC: Defang"
        
    def execute(self) -> list:
        """Execute defanging on all parsed IP/URL/domain observables.

        Applies defanging transformations to make IoCs safe for display.

        Returns:
            dict[str, str]: Keys are original observables, values are defanged
                versions.
        """
        observables = []
        self.results = {}
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            defanged = observable.replace(".","[.]")
            defanged = re.sub("^http","hxxp", defanged)
            self.results[observable] = defanged
        return self.results

    def __str__(self):
        """Return human-readable representation of defanged IoCs.

        Calls :meth:`execute` and formats output as one defanged IoC per line.

        Returns:
            str: Defanged observables, one per line.
        """
        self.execute()
        return  "\r\n".join(self.results.values())

class fangAction(actionInterface):
    r"""Refang (restore) defanged URLs, domains, and IP addresses.

    Reverses defanging by converting [.] back to . and hxxp back to http.
    Also handles [:://] to :// conversion. Restores IoCs to active format.

    Supported Types:
        ip, url, domain

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> parser = URLParser("hxxp://malicious[.]example[.]com/payload")
        >>> action = fangAction({"url": parser})
        >>> print(action)
        http://malicious.example.com/payload

        >>> from userTypeParser.IPParser import ipv4Parser
        >>> parser = ipv4Parser("192[.]168[.]1[.]1")
        >>> action = fangAction({"ip": parser})
        >>> print(action)
        192.168.1.1
    """

    def __init__(self, parsers = {}, supportedType = {"ip","url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "IoC: Refang"
        
    def execute(self) :
        """Execute refanging on all parsed IP/URL/domain observables.

        Applies refanging transformations to restore IoCs to active format.

        Returns:
            dict[str, str]: Keys are original defanged observables, values are
                refanged versions.
        """
        observables = []
        self.results = {}
        for parsertype in self.supportedType:
            observables += self.get_observables().get(parsertype, [])
        for observable in set(observables):
            fanged = observable.replace("[.]",".")
            fanged = re.sub(r"(\[:/?/?\])","://", fanged)
            fanged = re.sub("^hxxp","http", fanged)
            self.results[observable] = fanged

    def __str__(self):
        """Return human-readable representation of refanged IoCs.

        Calls :meth:`execute` and formats output as one refanged IoC per line.

        Returns:
            str: Refanged observables, one per line.
        """
        self.execute()
        return  "\r\n".join(self.results.values())

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\ngoogle.com\na"
    text_parser = domainParser(data)
    a = str(defangAction({'domain':text_parser},["domain"]))
    print(a)
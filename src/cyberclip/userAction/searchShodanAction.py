try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json
import time

import shodan

"""A action module, to open search observables contained in a text in Shodan."""


class searchInShodanAction(actionInterface):
    r"""Search IP addresses using the Shodan API.

    Queries Shodan for detailed information about IP addresses including open
    ports, services, vulnerabilities, and banners. Rate-limits requests for
    free accounts.

    Supported Types:
        ip

    Configuration:
        Requires the following in ``.env``::

            Shodan:
            - API_KEY: <your Shodan API key>

    Network Activity:
        Makes requests to: api.shodan.io

    Parameters:
        Allow bulk search (boolean): Use bulk search API (requires paid plan).
            Default: False
        Free account (boolean): Add 1-second delay between requests to avoid
            rate limits on free accounts.
            Default: False

    Example:
        >>> from userTypeParser.IPParser import ipv4Parser
        >>> parser = ipv4Parser("8.8.8.8")
        >>> action = searchInShodanAction({"ip": parser})
        >>> results = action.execute()
        >>> print(results["8.8.8.8"]["org"])
        Google LLC

    Note:
        Free accounts have rate limits. Enable "Free account" parameter to
        automatically wait 1 second between requests.
    """

    def __init__(
        self,
        parsers={},
        supportedType={"ip"},
        complex_param={
            "Allow bulk search": {"type": "boolean", "value": False},
            "Free account": {"type": "boolean", "value": False},
        },
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Shodan: Search IP"
        self.indicators = "🔑"
        self.load_conf("Shodan")
        if self.conf.get("API_KEY", ""):
            self.api = shodan.Shodan(self.conf.get("API_KEY", ""))
        else:
            self.api = None

    def execute(self) -> object:
        """Execute Shodan lookups on all parsed IP observables.

        Queries Shodan API for each IP with rate limiting if configured.

        Returns:
            dict[str, dict]: Keys are IP addresses, values are Shodan host
                information dictionaries.
        """
        self.results = {}
        self.observables = self.get_observables()
        if self.api:
            if self.observables.get("ip"):
                if not self.get_param_value("Allow bulk search"):
                    for ip in self.observables.get("ip"):
                        try:
                            self.results[ip] = self.api.host(ip)
                            if self.get_param_value("Free account"):
                                time.sleep(1.1)
                        except:
                            pass
                else:
                    data = self.api.host(self.observables.get("ip"))
                    for info in data:
                        self.results[info["ip_str"]] = info
        return self.results

    def __str__(self):
        """Return human-readable representation of Shodan results.

        Calls :meth:`execute` and formats output as JSON per IP.

        Returns:
            str: JSON-formatted Shodan data, one IP per line.
        """
        self.execute()
        return "\n".join(f"{json.dumps(v)}" for k, v in self.results.items())


if __name__ == "__main__":
    from userTypeParser.IPParser import ipv4Parser

    data = (
        "127.0.0.1, 206.168.89.216, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    )
    parser = ipv4Parser(data)
    a = str(searchInShodanAction({"ip": parser}, ["ip"]))
    print(a, parser.extract())

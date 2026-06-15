try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

QUERY_TEMPLATES = {
    "urlscan": {
        "ip": [
            {"single": 'ip:"{obs}"',       "agg": "ip:({items})",          "item": '"{obs}"', "sep": " OR "},
            {"single": 'page.ip:"{obs}"',  "agg": "page.ip:({items})",     "item": '"{obs}"', "sep": " OR "},
        ],
        "domain": [
            {"single": "domain:{obs}",       "agg": "domain:({items})",      "item": "{obs}", "sep": " OR "},
            {"single": "page.domain:{obs}",  "agg": "page.domain:({items})", "item": "{obs}", "sep": " OR "},
            {"single": "task.domain:{obs}",  "agg": "task.domain:({items})", "item": "{obs}", "sep": " OR "},
        ],
        "url": [
            {"single": 'page.url:"{obs}"', "agg": 'page.url:({items})', "item": '"{obs}"', "sep": " OR "},
            {"single": 'task.url:"{obs}"', "agg": 'task.url:({items})', "item": '"{obs}"', "sep": " OR "},
        ],
        "md5":    [{"single": "hash:{obs}", "agg": "hash:({items})", "item": "{obs}", "sep": " OR "}],
        "sha1":   [{"single": "hash:{obs}", "agg": "hash:({items})", "item": "{obs}", "sep": " OR "}],
        "sha256": [{"single": "hash:{obs}", "agg": "hash:({items})", "item": "{obs}", "sep": " OR "}],
    },
    "censys": {
        "ip": [
            {"single": "host.ip:{obs}",                                  "agg": 'host.ip: {{{items}}}',                                  "item": '"{obs}"', "sep": ", "},
        ],
        "domain": [
            {"single": "host.dns.names:{obs}",                           "agg": 'host.dns.names: {{{items}}}',                                "item": '"{obs}"', "sep": ", "},
            {"single": "web.hostname:{obs}",                           "agg": 'web.hostname: {{{items}}}',                                "item": '"{obs}"', "sep": ", "},
            {"single": "host.services.cert.names:{obs}", "agg": 'host.services.cert.names: {{{items}}}', "item": '"{obs}"', "sep": ", "},
            {"single": "web.cert.names:{obs}", "agg": 'web.cert.names: {{{items}}}', "item": '"{obs}"', "sep": ", "},
        ],
        "sha256": [
            {"single": "services.tls.certificates.leaf_data.fingerprint:{obs}", "agg": 'services.tls.certificates.leaf_data.fingerprint: {{{items}}}', "item": '"{obs}"', "sep": ", "},
        ],
    },
    "shodan": {
        "ip": [
            {"single": "ip:{obs}", "agg": 'ip:{items}', "item": '{obs}', "sep": ","},
        ],
        "cidr": [
            {"single": "net:{obs}","agg": 'net:{items}', "item": '{obs}', "sep": ","},
        ],
        "domain": [
            {"single": "hostname:{obs}","agg": 'hostname:{items}', "item": '{obs}', "sep": ","},
            {"single": "ssl.cert.subject.cn:{obs}","agg": 'ssl.cert.subject.cn:{items}', "item": '{obs}', "sep": ","},
        ],
        "url":    [{"single": 'http.html:"{obs}"'}],
        "sha256": [{"single": "ssl.cert.fingerprint:{obs}"}],
    },
    "virustotal": {
        "ip":     [{"single": "{obs}"},
                   {"single": "behaviour_network:{obs}", "sep": " "}],
        "domain": [{"single": "{obs}"},
                    {"single": "behaviour_network:{obs}", "sep": " "}],
    },
    "modat": {
        "ip":     [{"single": "{obs}", "agg": "ip={{{items}}}",     "item": "{obs}", "sep": " or "}],
        "domain": [{"single": "domain={obs}"}],
    },
}

DEFAULT_PARAMS = {
    "Platforms": {
        "type": "fixedlist",
        "choices": list(QUERY_TEMPLATES),
        "value": list(QUERY_TEMPLATES),
    },
    "Aggregate": {"type": "bool", "value": True},
}

SUPPORTED_TYPES = {"ip", "cidr", "domain", "url", "md5", "sha1", "sha256"}


class CTIQueryAction(actionInterface):
    """Generate search queries for threat intelligence platforms. Given IoCs (IPs, domains, URLs, hashes), produces platform-specific query strings for URLScan, Censys, Shodan, VirusTotal, and Modat.

    Multiple query variants are generated per platform to cover different
    search fields (host, DNS, certificate, web properties).

    Options:
    - Platforms: select which platforms to generate queries for
    - Aggregate: combine observables of the same type into a single query per platform
    """

    def __init__(self, parsers={}, supportedType=SUPPORTED_TYPES, complex_param=DEFAULT_PARAMS):
        super().__init__(parsers=parsers, supportedType=supportedType, complex_param=complex_param)
        self.description = "CTI: Generate Queries"

    def _format_single(self, obs, obs_type, platform):
        templates = QUERY_TEMPLATES.get(platform, {})
        entries = templates.get(obs_type, [{"single": "{obs}"}])
        return [entry["single"].format(obs=obs) for entry in entries]

    def _format_aggregate(self, observables, obs_type, platform):
        templates = QUERY_TEMPLATES.get(platform, {})
        entries = templates.get(obs_type, [{"single": "{obs}"}])
        results = []
        for entry in entries:
            if "agg" in entry:
                item_fmt = entry.get("item", "{obs}")
                sep = entry.get("sep", " OR ")
                items = sep.join(item_fmt.format(obs=obs) for obs in observables)
                results.append(entry["agg"].format(items=items))
            else:
                results.append(" OR ".join(entry["single"].format(obs=obs) for obs in observables))
        return results

    def execute(self) -> dict:
        self.results = {}
        self.observables = self.get_observables()

        platforms = self.get_param_value("Platforms")
        if isinstance(platforms, str):
            platforms = [p.strip() for p in platforms.split(",")]

        aggregate = self.get_param_value("Aggregate")

        for platform in platforms:
            queries = []
            for obs_type, observables in self.observables.items():
                obs_list = list(set(observables))
                if not obs_list:
                    continue
                if aggregate:
                    queries.extend(self._format_aggregate(obs_list, obs_type, platform))
                else:
                    for obs in obs_list:
                        queries.extend(self._format_single(obs, obs_type, platform))
            self.results[platform] = queries

        return self.results

    def __str__(self):
        self.execute()
        lines = []
        for platform, queries in self.results.items():
            lines.append(f"=== {platform.upper()} ===")
            lines.extend(queries)
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    from userTypeParser.IPParser import ipv4Parser
    from userTypeParser.domainParser import domainParser

    data = "8.8.8.8 1.1.1.1 9.9.9.9"
    ip_parser = ipv4Parser(data)
    domain_data = "google.com example.com"
    domain_parser = domainParser(domain_data)

    action = CTIQueryAction({"ip": ip_parser, "domain": domain_parser})
    print(action)

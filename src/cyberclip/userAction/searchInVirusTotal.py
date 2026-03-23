try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json

import requests

"""Search observables in Virus Total."""

DEFAULT_PARAMS = {
    "Relationships": {
        "type": "tags",
        "value": [
            "submissions",
            "contacted_urls",
            "contacted_domains",
            "contacted_ips",
            "dropped_files",
            "bundled_files",
            "itw_urls",
            "submissions",
            "execution_parents",
        ],
    },
}


class searchInVirusTotalAction(actionInterface):
    """Search ip, domain, MD5, SHA1 and SHA256 with the Virus Total API. Results are returned in JSON format. The configuration should be passed in the config file.

    A parameter could be passed :

        - `Relationships` a list of relationships to query. For each relationship, the full relationship object content is fetched.
          Be careful: each additional relationship consumes an API credit.
          Available relationships: tags, contacted_urls, contacted_domains, contacted_ips, dropped_files, bundled_files, itw_urls, submissions, execution_parents
          Full relationship data will be stored under `$.data.<relationship_name>` key for each observable.


    A configuration is needed :

    ```yaml
    VirusTotal:
    - api_key: <VT API Key>
    ```
    """

    def __init__(
        self,
        parsers={},
        supportedType={"ip", "domain", "md5", "sha1", "sha256"},
        complex_param=DEFAULT_PARAMS,
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Virus Total: Search all obsevables."
        self.indicators = "🔑"
        self.lines = []
        self.load_conf("VirusTotal")
        API_KEY = self.conf.get("API_KEY", "")
        self.headers = {"accept": "application/json", "x-apikey": API_KEY}

    def execute(self):
        """Execute VirusTotal lookups for all parsed observables.

        Queries the VirusTotal API for each observable (IP, domain, or file hash)
        and retrieves analysis results including optional relationship data.
        For each relationship, fetches the complete objects instead of just descriptors.

        Returns:
            dict[str, Any]: Keys are observable strings, values are VirusTotal
                API response JSON objects with full relationship content.
        """
        self.observables = self.get_observables()
        self.results = {}

        relationships = (
            self.get_param_value("Relationships")
            if self.get_param_value("Relationships")
            else []
        )

        for obs_type in self.supportedType:
            if obs_type == "ip" and (observables := self.observables.get(obs_type, [])):
                for ip in observables:
                    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[ip] = response.json()
                        # Fetch full relationship content
                        self._fetch_relationships(ip, "ip_addresses", relationships)
                    except:
                        self.results[ip] = {}

            if obs_type == "domain" and (
                observables := self.observables.get(obs_type, [])
            ):
                for domain in observables:
                    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[domain] = response.json()
                        # Fetch full relationship content
                        self._fetch_relationships(domain, "domains", relationships)
                    except:
                        self.results[domain] = {}

            if obs_type in ["md5", "sha1", "sha256"] and (
                observables := self.observables.get(obs_type, [])
            ):
                for file_hash in observables:
                    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[file_hash] = response.json()
                        # Fetch full relationship content
                        self._fetch_relationships(file_hash, "files", relationships)
                    except:
                        self.results[file_hash] = {}

        return list(self.results.values())

    def _fetch_relationships(self, observable, collection, relationships):
        """Fetch full relationship content for an observable.

        Args:
            observable: The observable identifier (IP, domain, or hash)
            collection: The API collection name (ip_addresses, domains, or files)
            relationships: List of relationship names to fetch
        """
        if not relationships:
            return

        if observable not in self.results:
            self.results[observable] = {}

        if "data" not in self.results[observable]:
            self.results[observable]["data"] = {}

        for relationship in relationships:
            url = f"https://www.virustotal.com/api/v3/{collection}/{observable}/{relationship}"
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    rel_data = response.json()
                    # Store the full relationship data
                    self.results[observable]["data"][relationship] = rel_data.get(
                        "data", []
                    )
            except Exception:
                # Silently skip failed relationship fetches
                pass

    def __str__(self):
        """Return human-readable representation of VirusTotal results.

        Calls :meth:`execute` and formats output as indented JSON.

        Returns:
            str: Formatted JSON containing all VirusTotal lookup results.
        """
        self.execute()
        return json.dumps(list(self.results.values()), indent=3)


if __name__ == "__main__":
    from userTypeParser.MD5Parser import md5Parser

    data = "127.0.0.1, 124.0.12.23, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    parser = md5Parser(data)
    a = str(
        searchInVirusTotalAction({"md5": parser}, ["md5"], complex_param=DEFAULT_PARAMS)
    )

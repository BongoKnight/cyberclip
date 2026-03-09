try:
    from userAction.actionInterface import actionInterface
except ImportError:
    from actionInterface import actionInterface

import time
import requests
import ipaddress
from pathlib import Path


class TorExitIPAction(actionInterface):
    """Check whether an IP (IPv4/IPv6) is present in a Tor exit node list."""

    TOR_EXITS_URL = "https://raw.githubusercontent.com/alireza-rezaee/tor-nodes/refs/heads/main/latest.exits.csv"

    CACHE_SECONDS = 6 * 3600
    _tor_exit_set = None
    _tor_exit_set_ts = 0

    def __init__(self, parsers={}, supportedType={"ip", "ipv6"}, complex_param={}):
        super().__init__(parsers=parsers, supportedType=supportedType, complex_param=complex_param)
        self.description = "IP: Tor Exit Node"
        self.indicators = "📑"
        self.results = {}

    @staticmethod
    def _normalize_ip(s: str) -> str:
        """Return a normalized IP string or empty string if invalid."""
        try:
            return str(ipaddress.ip_address(s.strip()))
        except Exception:
            return ""

    @classmethod
    def _cache_file(cls) -> Path:
        return Path(__file__).parent / "../data/tor_exits.csv"

    @classmethod
    def load_tor_exit_set(cls) -> set[str]:
        """
        Load tor exit IPs into a set, with:
        - in-memory cache (fast)
        - on-disk cache (works across runs)
        - periodic refresh

        Returns:
            set[str]: normalized IP strings
        """
        now = time.time()

        if cls._tor_exit_set is not None and (now - cls._tor_exit_set_ts) < cls.CACHE_SECONDS:
            return cls._tor_exit_set

        cache_path = cls._cache_file()

        try:
            if cache_path.exists() and (now - cache_path.stat().st_mtime) < cls.CACHE_SECONDS:
                text = cache_path.read_text(encoding="utf-8", errors="ignore")
                cls._tor_exit_set = cls._parse_csv_to_ip_set(text)
                cls._tor_exit_set_ts = now
                return cls._tor_exit_set
        except Exception:
            pass

        try:
            r = requests.get(cls.TOR_EXITS_URL, timeout=15)
            r.raise_for_status()
            text = r.text

            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(text, encoding="utf-8")

            cls._tor_exit_set = cls._parse_csv_to_ip_set(text)
            cls._tor_exit_set_ts = now
            return cls._tor_exit_set
        except Exception as e:
            try:
                if cache_path.exists():
                    text = cache_path.read_text(encoding="utf-8", errors="ignore")
                    cls._tor_exit_set = cls._parse_csv_to_ip_set(text)
                    cls._tor_exit_set_ts = now
                    return cls._tor_exit_set
            except Exception:
                pass

            print(f"[TorExitIPAction] Error fetching tor exit list: {e}")
            cls._tor_exit_set = set()
            cls._tor_exit_set_ts = now
            return cls._tor_exit_set

    @classmethod
    def _parse_csv_to_ip_set(cls, csv_text: str) -> set[str]:
        """
        Parse the CSV text and extract the ipaddr column (2nd column).

        Handles:
        - header line
        - extra spaces
        - invalid lines
        """
        ips = set()
        for line in csv_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("fingerprint"):
                continue

            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue

            ip_str = cls._normalize_ip(parts[1])
            if ip_str:
                ips.add(ip_str)

        return ips

    def execute(self):
        self.results = {}
        self.observables = self.get_observables()

        ips = (self.observables.get("ip", []) or []) + (self.observables.get("ipv6", []) or [])
        ips = [self._normalize_ip(ip) for ip in ips]
        ips = [ip for ip in ips if ip]

        tor_exits = self.load_tor_exit_set()

        self.results = {ip: ("TOR_EXIT" if ip in tor_exits else "OK") for ip in ips}
        return self.results

    def __str__(self):
        self.execute()
        tor_only = [ip for ip, status in self.results.items() if status == "TOR_EXIT"]
        return "\n".join(tor_only) if tor_only else "No Tor exit IP found"
    

if __name__ == "__main__":
    try:
        from userTypeParser.IPParser import IPParser

        data = "204.137.14.106 8.8.8.8 2606:4700:4700::1111"
        parser = IPParser(data)

        action = TorExitIPAction(parsers={"ip": parser, "ipv6": parser})
        print("Observables:", action.get_observables())
        print("Execute:", action.execute())
        print("String output:\n", str(action))

    except Exception as e:
        print("Could not import IPParser, using dummy parser. Error:", e)

        class DummyParser:
            parsertype = "ip"
            def __init__(self, items):
                self._items = items
            def extract(self):
                return self._items

        dummy = DummyParser(["204.137.14.106", "8.8.8.8"])
        action = TorExitIPAction(parsers={"ip": dummy})
        print("Execute:", action.execute())
        print("String output:\n", str(action))
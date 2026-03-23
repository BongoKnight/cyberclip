---
title: API Reference
---

# Action Configuration Reference

This page documents the configuration systems used throughout CyberClip actions and parsers.

## complex_param Type Reference

The `complex_param` dictionary defines user-configurable parameters for actions. Each parameter key maps to a configuration dictionary that controls how the parameter appears in the TUI and what values it accepts.

### Parameter Type Schema

| Type | TUI Widget | Value Format | Extra Keys | Example |
|------|-----------|-------------|------------|---------|
| `text` | Single-line input | `str` | - | `{"Limit": {"type": "text", "value": "100"}}` |
| `tags` | Tag input (multi-entry) | `list[str]` | - | `{"Records": {"type": "tags", "value": ["A", "TXT"]}}` |
| `bool` | Checkbox | `bool` | - | `{"HTTPS": {"type": "bool", "value": True}}` |
| `list` | Dropdown (single-select) | `str` | `choices` (list) | `{"Lang": {"type": "list", "choices": ["EN", "FR"], "value": "EN"}}` |
| `fixedlist` | Multi-select checkboxes | `list[str]` | `choices` (list) | `{"Relations": {"type": "fixedlist", "choices": ["passivedns", "whois"], "value": []}}` |
| `json` | JSON editor | `list` or `dict` | - | `{"Selectors": {"type": "json", "value": []}}` |
| `longtext` | Multi-line textarea | `str` | - | `{"Headers": {"type": "longtext", "value": ""}}` |
| `save` | File save dialog | `str` (path) | - | `{"Save as": {"type": "save", "value": "./out.txt"}}` |

### Type Details

#### text
Single-line text input for short strings like limits, names, or IDs.

```python
complex_param = {
    "API_Limit": {
        "type": "text",
        "value": "100"
    }
}
```

#### tags
Multi-entry tag input where users can add/remove individual string values. Useful for lists of DNS record types, file extensions, etc.

```python
complex_param = {
    "DNS_Records": {
        "type": "tags",
        "value": ["A", "AAAA", "TXT", "MX"]
    }
}
```

#### bool
Checkbox for true/false options.

```python
complex_param = {
    "Use_HTTPS": {
        "type": "bool",
        "value": True
    }
}
```

#### list
Dropdown menu where users select one option from predefined choices.

```python
complex_param = {
    "Output_Format": {
        "type": "list",
        "choices": ["JSON", "CSV", "TSV"],
        "value": "JSON"
    }
}
```

#### fixedlist
Multi-select interface where users can choose multiple options from predefined choices.

```python
complex_param = {
    "VirusTotal_Relations": {
        "type": "fixedlist",
        "choices": [
            "downloaded_files", "contacted_domains",
            "contacted_ips", "embedded_urls"
        ],
        "value": ["contacted_domains", "contacted_ips"]
    }
}
```

#### json
JSON editor for complex structured data like lists of objects or nested configurations.

```python
complex_param = {
    "CSS_Selectors": {
        "type": "json",
        "value": [
            {"selector": ".title", "attribute": "text"},
            {"selector": "a", "attribute": "href"}
        ]
    }
}
```

#### longtext
Multi-line text area for longer text inputs like HTTP headers, templates, or notes.

```python
complex_param = {
    "Custom_Headers": {
        "type": "longtext",
        "value": "User-Agent: CyberClip/1.0\nAccept: application/json"
    }
}
```

#### save
File save dialog that opens a file picker. Returns the selected file path as a string.

```python
complex_param = {
    "Output_File": {
        "type": "save",
        "value": "./output.txt"
    }
}
```

---

## Indicator Emoji Reference

Actions use indicator emojis in their `indicators` attribute to communicate requirements and warnings to users at a glance.

| Emoji | Meaning | When to Use | Example |
|-------|---------|-------------|---------|
| 🔑 | Requires API key | Action needs credentials configured in `.env` | VirusTotal, Shodan, URLScan lookups |
| 📑 | Requires data file | Action loads external data files at runtime | GeoIP databases, threat feeds |
| 🌍 | Network request | Action makes HTTP requests to external services | DNS lookups, API calls, web scraping |
| 🚩 | Dangerous operation | Potentially risky or irreversible operations | File deletion, URL opening, code execution |
| 🐌 | Slow operation | May take significant time to complete | Bulk API requests, large file processing |

### Usage Examples

**Single indicator:**
```python
class VirusTotalAction(actionInterface,
                       description="VirusTotal Lookup",
                       supportedType={"domain", "ip", "hash"},
                       indicators="🔑"):  # Requires API key
    pass
```

**Multiple indicators:**
```python
class ShodanAction(actionInterface,
                   description="Shodan IP Lookup",
                   supportedType={"ip"},
                   indicators="🔑🌍"):  # Requires API key + makes network requests
    pass
```

**Dangerous operations:**
```python
class URLOpenAction(actionInterface,
                    description="Open URLs in Browser",
                    supportedType={"url"},
                    indicators="🚩"):  # Potentially dangerous (opens external URLs)
    pass
```

### Guidelines

- **Combine indicators** when multiple apply (e.g., "🔑🌍" for authenticated API calls)
- **Use 🚩 sparingly** - only for operations that could cause harm or data loss
- **Document requirements** - Always document what `.env` keys are needed for 🔑
- **Be honest about speed** - If users will wait >5 seconds, use 🐌

---

## Parser Type Registry

This table maps all built-in parser types to their classes and what they detect. Use these `parsertype` values in action `supportedType` sets.

| Parser Type | Class Name | Detects | Defanging Support | Example Match |
|-------------|-----------|---------|-------------------|---------------|
| `ip` | `ipv4Parser` | IPv4 addresses | ✓ (converts `[.]` to `.`) | `192.168.1.1` |
| `cidr` | `CIDRParser` | CIDR notation | ✓ (converts `[.]` to `.`) | `10.0.0.0/8` |
| `ipv6` | `ipv6Parser` | IPv6 addresses | ✓ (converts `[.]` to `.`) | `2001:0db8::1` |
| `domain` | `domainParser` | Domain names with TLD validation | ✓ (converts `[.]` to `.`) | `example.com` |
| `url` | `URLParser` | HTTP/HTTPS URLs | ✓ (handles `hxxp`, `[://]`, `[.]`) | `https://example.com/path` |
| `mail` | `mailParser` | Email addresses | ✗ | `user@example.com` |
| `md5` | `MD5Parser` | MD5 hashes (32 hex chars) | ✗ | `5d41402abc4b2a76b9719d911017c592` |
| `sha1` | `SHA1Parser` | SHA1 hashes (40 hex chars) | ✗ | `aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d` |
| `sha256` | `SHA256Parser` | SHA256 hashes (64 hex chars) | ✗ | `2c26b46b68ffc68ff99b453c1d30413413422d706...` |
| `cve` | `CVEParser` | CVE identifiers | ✗ | `CVE-2021-44228` |
| `mitre` | `MitreParser` | MITRE ATT&CK TTPs | ✗ | `T1566.001` |
| `asnum` | `ASNumberParser` | Autonomous System Numbers | ✗ | `AS15169` |
| `rfc` | `RFCParser` | RFC document numbers | ✗ | `RFC 9110` |
| `b64` | `B64Parser` | Base64 strings (full lines) | ✗ | `dG90bw==` |
| `ja4` | `JA4Parser` | JA4 fingerprints | ✗ | `t13d1517h2_8daaf6152771_e5627efa2ab1` |
| `analytics` | `AnalyticsIdParser` | Google Analytics IDs | ✗ | `UA-12345678-1` |
| `phone` | `PhoneParser` | Phone numbers | ✗ | `+1-555-123-4567` |
| `filename` | `filenameParser` | File paths (checks filesystem) | ✗ | `/etc/passwd` |
| `html` | `HtmlParser` | HTML content (uses BeautifulSoup) | ✗ | `<b>text</b>` |
| `json` | `JsonParser` | JSON data (validates with json.loads) | ✗ | `{"key": "value"}` |
| `yaml` | `YamlParser` | YAML data (validates with yaml.safe_load) | ✗ | `key: value` |
| `csv` | `csvParser` | CSV/TSV data (auto-detects delimiter) | ✗ | `col1,col2,col3` |
| `commonlog` | `CommonLogParser` | Common Log Format | ✗ | `127.0.0.1 - - [date] "GET / HTTP/1.1" 200 -` |
| `combinedlog` | `CombinedLogParser` | Combined Log Format | ✗ | (Common Log + referer + user-agent) |
| `text` | `TextParser` | Any text (always matches) | ✗ | (any string) |

### Notes on Parser Types

- **Defanging**: Several parsers automatically normalize defanged indicators (e.g., `192[.]168[.]1[.]1` → `192.168.1.1`)
- **Validation**: Some parsers validate format (e.g., `domainParser` checks TLD validity, `JsonParser` validates JSON syntax)
- **Multiple parsers per text**: CyberClip runs all parsers on input text; one text can match multiple parser types
- **Custom parsers**: Add your own by creating a class in `userTypeParser/private/` (see [CreateNewParser.md](CreateNewParser.md))

---

## Using Reference Information in Code

### Example: Multi-Type Action with complex_param

```python
class DNSLookupAction(actionInterface,
                      description="DNS Lookup",
                      supportedType={"domain", "ip"},
                      indicators="🌍"):
    """Perform DNS lookups with configurable record types.

    Supported Types:
        domain, ip

    Network Activity:
        Makes DNS queries to configured resolvers.

    Parameters:
        Record_Types (tags): DNS record types to query (A, AAAA, MX, TXT, etc.)
        Resolver (text): DNS resolver IP address
        Include_Reverse (bool): Perform reverse DNS lookups for IPs
    """

    def __init__(self, parsers={}, **kwargs):
        # Define complex parameters
        complex_param = {
            "Record_Types": {
                "type": "tags",
                "value": ["A", "AAAA", "MX", "TXT"]
            },
            "Resolver": {
                "type": "text",
                "value": "8.8.8.8"
            },
            "Include_Reverse": {
                "type": "bool",
                "value": True
            }
        }

        super().__init__(
            parsers=parsers,
            complex_param=complex_param,
            **kwargs
        )

    def execute(self):
        # Access parameter values
        record_types = self.get_param_value("Record_Types")
        resolver = self.get_param_value("Resolver")
        include_reverse = self.get_param_value("Include_Reverse")

        self.get_observables()

        # Process domains
        for domain in self.observables.get("domain", []):
            # Perform lookups...
            pass

        # Process IPs (if Include_Reverse is enabled)
        if include_reverse:
            for ip in self.observables.get("ip", []):
                # Perform reverse lookup...
                pass

        return self.results
```

---

## See Also

- [CreateNewParser.md](CreateNewParser.md) - Tutorial for creating custom parsers
- [CreateNewAction.md](CreateNewAction.md) - Tutorial for creating custom actions
<!-- - [ParserInterface API](../reference/userTypeParser/ParserInterface.md) - Base parser class documentation
- [actionInterface API](../reference/userAction/actionInterface.md) - Base action class documentation -->

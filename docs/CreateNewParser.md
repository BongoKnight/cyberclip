---
title: Tutorial - Create a new parser
---

# Goal

This tutorial explains in depth the process to create a new parser. We will create a new parser for extracting MAC addresses (network hardware addresses) from text.

MAC addresses are typically formatted as six groups of two hexadecimal digits separated by colons or hyphens (e.g., `00:1A:2B:3C:4D:5E` or `00-1A-2B-3C-4D-5E`).

# Prerequisites

Before creating a parser, you should:

- Have basic knowledge of regular expressions (regex)
- Understand Python classes and inheritance
- Be familiar with the `re` module for pattern matching

# Understanding ParserInterface

All parsers in CyberClip inherit from the `ParserInterface` base class. This interface defines three key attributes and two required methods:

**Attributes:**

- `parsertype` (str): A unique lowercase identifier for your parser (e.g., "ip", "domain", "mac")
- `text` (str): The input text to parse
- `objects` (list): Stores extracted objects after calling `extract()`

**Required Methods:**

- `contains()` → bool: Returns `True` if the text contains at least one match
- `extract()` → list: Returns a list of all extracted matches from the text

# Step-by-Step: Creating a MAC Address Parser

## Step 1: Create the Parser File

Create a new file called `MacAddressParser.py` in the `userTypeParser/private/` directory of your CyberClip installation.

**Why private/?** The `private/` directory is for custom parsers that won't be tracked by git, allowing you to extend CyberClip without modifying core files.

## Step 2: Import ParserInterface

Start by importing the base class:

```python
import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface
```

The try/except block handles different import contexts (running CyberClip vs testing the parser standalone).

## Step 3: Define Your Parser Class

Create your parser class with a comprehensive docstring:

```python
class MacAddressParser(ParserInterface):
    """Parse and extract MAC addresses from text.

    MAC addresses (Media Access Control addresses) are hardware identifiers
    for network interfaces, formatted as six groups of two hexadecimal digits.

    Regex Pattern:
        ``\\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\\b``

    Defanging Support:
        No. MAC addresses are not typically defanged.

    Example:
        ```python
        parser = MacAddressParser("No MAC here")
        parser.contains()
        False
        parser = MacAddressParser("Device MAC: 00:1A:2B:3C:4D:5E")
        parser.contains()
        True
        parser.extract()
        ['00:1A:2B:3C:4D:5E']
        ```
    """

    def __init__(self, text: str, parsertype="mac"):
        super().__init__(text, parsertype="mac")
```

**Key points:**

- Class name must contain "Parser" to be auto-discovered by CyberClip
- The `parsertype` should be a short, descriptive lowercase string
- Document the regex pattern and whether defanging is supported
- Include working examples in the docstring

## Step 4: Implement the contains() Method

This method checks if at least one MAC address exists in the text:

```python
    def contains(self) -> bool:
        """Check whether the text contains at least one MAC address.

        Returns:
            bool: True if at least one MAC address is found in the text.
        """
        if re.search(r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b", self.text):
            return True
        else:
            return False
```

**Best practice:** Use `re.search()` for contains() since you only need to know if a match exists (stops at first match, more efficient).

## Step 5: Implement the extract() Method

This method extracts all MAC addresses from the text:

```python
    def extract(self) -> list[str]:
        """Extract all MAC address instances from the text.

        Returns:
            list[str]: A list of extracted MAC address values.
        """
        mac_iter = re.finditer(r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b", self.text)
        mac_addresses = [mac.group() for mac in mac_iter]
        self.objects = mac_addresses
        return mac_addresses
```

**Key points:**

- Use `re.finditer()` to get all matches (returns an iterator of match objects)
- Extract the matched text using `.group()`
- Store results in `self.objects` for compatibility with the CyberClip framework
- Return the list of extracted values

# Regex Best Practices

## 1. Testing Your Pattern

Before implementing, test your regex pattern using online tools like [regex101.com](https://regex101.com):

- Test with positive examples (text that should match)
- Test with negative examples (text that should not match)
- Test edge cases (unusual but valid formats)

## 2. Word Boundaries

Use `\b` word boundaries to avoid partial matches:

```python
# Good: \b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b
# Matches: "00:1A:2B:3C:4D:5E" ✓

# Bad: ([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})
# Would match inside: "X00:1A:2B:3C:4D:5EY" ✗
```

## 3. Case Sensitivity

Use character classes like `[A-Fa-f]` to match both uppercase and lowercase:

```python
[0-9A-Fa-f]  # Matches: 0-9, A-F, a-f
```

## 4. Escape Special Characters

Remember to escape regex special characters:

- `.` becomes `\.` (literal period)
- `[` becomes `\[` (literal bracket)
- `\` becomes `\\` (literal backslash)

# Handling Defanged Indicators

Some observables (IPs, domains, URLs) may be "defanged" to prevent accidental clicks or automatic processing. For example:

- `192.168.1.1` → `192[.]168[.]1[.]1`
- `example.com` → `example[.]com`
- `http://evil.com` → `hxxp://evil[.]com`

If your parser needs to handle defanging:

```python
def extract(self) -> list[str]:
    """Extract all domains from text.

    Defanged notation (e.g., example[.]com) is normalized to standard format.

    Returns:
        list[str]: A list of extracted domain values.
    """
    # First, normalize defanged notation
    normalized_text = self.text.replace('[.]', '.')

    # Then extract from normalized text
    domain_iter = re.finditer(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b", normalized_text, re.IGNORECASE)
    domains = [domain.group() for domain in domain_iter]
    self.objects = domains
    return domains
```

**When to add defanging support:**

- IPs and domains: Yes (commonly defanged in threat intelligence)
- URLs: Yes (commonly defanged)
- Hashes, CVEs, MAC addresses: No (rarely defanged)

# Testing Your Parser

Add a test block at the end of your parser file:

```python
if __name__ == "__main__":
    # Test case 1: No MAC addresses
    parser1 = MacAddressParser("This text has no MAC addresses")
    print(f"Test 1 - contains: {parser1.contains()}")  # Should be False
    print(f"Test 1 - extract: {parser1.extract()}")    # Should be []

    # Test case 2: Single MAC address
    parser2 = MacAddressParser("Device MAC: 00:1A:2B:3C:4D:5E")
    print(f"Test 2 - contains: {parser2.contains()}")  # Should be True
    print(f"Test 2 - extract: {parser2.extract()}")    # Should be ['00:1A:2B:3C:4D:5E']

    # Test case 3: Multiple MAC addresses
    parser3 = MacAddressParser("MACs: 00:1A:2B:3C:4D:5E and AA-BB-CC-DD-EE-FF")
    print(f"Test 3 - contains: {parser3.contains()}")  # Should be True
    print(f"Test 3 - extract: {parser3.extract()}")    # Should be ['00:1A:2B:3C:4D:5E', 'AA-BB-CC-DD-EE-FF']

    # Test case 4: Mixed case
    parser4 = MacAddressParser("MAC: ab:cd:ef:12:34:56")
    print(f"Test 4 - contains: {parser4.contains()}")  # Should be True
    print(f"Test 4 - extract: {parser4.extract()}")    # Should be ['ab:cd:ef:12:34:56']
```

Run your parser standalone:

```bash
cd /path/to/cyberclip/src/cyberclip/userTypeParser/private/
python MacAddressParser.py
```

# Making Actions Use Your Parser

Once your parser is created, actions can use it by adding your `parsertype` to their `supportedType` set:

```python
class MyAction(actionInterface,
               description="Process MAC Addresses",
               supportedType={"mac"}):  # Add your parser type here

    def execute(self):
        self.get_observables()
        for mac in self.observables.get("mac", []):
            # Process each MAC address
            print(f"Processing: {mac}")
        return self.results
```

**Multi-type support:** Actions can support multiple parser types:

```python
supportedType={"ip", "domain", "mac"}  # Supports IPs, domains, and MACs
```

# Full Example Code

Here's the complete MAC address parser:

```python
import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class MacAddressParser(ParserInterface):
    """Parse and extract MAC addresses from text.

    MAC addresses (Media Access Control addresses) are hardware identifiers
    for network interfaces, formatted as six groups of two hexadecimal digits.

    Regex Pattern:
        ``\\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\\b``

    Defanging Support:
        No. MAC addresses are not typically defanged.

    Example:
        ```python
        parser = MacAddressParser("No MAC here")
        parser.contains()
        False
        parser = MacAddressParser("Device MAC: 00:1A:2B:3C:4D:5E")
        parser.contains()
        True
        parser.extract()
        ['00:1A:2B:3C:4D:5E']
        ```
    """

    def __init__(self, text: str, parsertype="mac"):
        super().__init__(text, parsertype="mac")

    def contains(self) -> bool:
        """Check whether the text contains at least one MAC address.

        Returns:
            bool: True if at least one MAC address is found in the text.
        """
        if re.search(r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b", self.text):
            return True
        else:
            return False

    def extract(self) -> list[str]:
        """Extract all MAC address instances from the text.

        Returns:
            list[str]: A list of extracted MAC address values.
        """
        mac_iter = re.finditer(r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b", self.text)
        mac_addresses = [mac.group() for mac in mac_iter]
        self.objects = mac_addresses
        return mac_addresses


if __name__ == "__main__":
    # Test case 1: No MAC addresses
    parser1 = MacAddressParser("This text has no MAC addresses")
    print(f"Test 1 - contains: {parser1.contains()}")
    print(f"Test 1 - extract: {parser1.extract()}")

    # Test case 2: Single MAC address
    parser2 = MacAddressParser("Device MAC: 00:1A:2B:3C:4D:5E")
    print(f"Test 2 - contains: {parser2.contains()}")
    print(f"Test 2 - extract: {parser2.extract()}")

    # Test case 3: Multiple MAC addresses
    parser3 = MacAddressParser("MACs: 00:1A:2B:3C:4D:5E and AA-BB-CC-DD-EE-FF")
    print(f"Test 3 - contains: {parser3.contains()}")
    print(f"Test 3 - extract: {parser3.extract()}")

    # Test case 4: Mixed case
    parser4 = MacAddressParser("MAC: ab:cd:ef:12:34:56")
    print(f"Test 4 - contains: {parser4.contains()}")
    print(f"Test 4 - extract: {parser4.extract()}")
```

# Next Steps

Now that you've created your parser:

1. **Test thoroughly** - Run the `if __name__ == "__main__":` block and verify all test cases pass
2. **Check auto-discovery** - Restart CyberClip and verify your parser is loaded (check logs)
3. **Create or modify actions** - Update actions to use your new parser type
4. **Add documentation** - Ensure your docstring is complete for API documentation generation

For more information, see:

<!-- - [ParserInterface API Reference](../reference/userTypeParser/ParserInterface.md)
- [Action Interface Documentation](../reference/userAction/actionInterface.md) -->
- [Reference Documentation](Reference.md) for parser type registry

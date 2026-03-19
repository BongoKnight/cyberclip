
# Introduction 

> Cyberclip is designed to detect and extract recognizable data from text inputs, enabling data transformation and enrichment for cybersecurity professionals. Tailored for cyber threat analysts and SOC operators, Cyberclip helps investigate and pivot around technical indicators such as domains, URLs, IP addresses, and file hashes. It features a simple terminal interface (TUI) that integrates with tools like UrlScan, OpenCTI, and VirusTotal. It can also be used to extract data from JSON, defang IoCs, and encode or decode data in formats like Hex, Base64, and URL encode and much more... In short, Cyberclip empowers investigators to perform quick checks and make informed decisions during investigations!
>
> User documentation: [https://bongoknight.github.io/cyberclip/Features%20tour/](https://bongoknight.github.io/cyberclip/Features%20tour/)

# .env file and variables

Variables that allows Cyberclip to authenticate itself against third-party API should be written in `/src/cyberclip/.env`:

```bash 
DATALAKE_EMAIL="<DATALAKE EMAIL>"
DATALAKE_PASSWORD="<DATALAKE PASSWORD>"
DEEPL_API-KEY="<DEEPL API-KEY>"
SHODAN_API-KEY="<SHODAN API KEY>"
URLSCAN_API-KEY="<URLSCAN API KEY>"
VIRUSTOTAL_API-KEY="<VIRUS TOTAL API KEY>"
```

# Installation

## Requirements

- Python 3.10+ (up to 3.13)
- Git (for source installation)
- Docker (for docker deployment)

## Quick Start

### Basic Installation (TUI only)

```bash
pip install cyberclip
```

### With Optional Features

```bash
# With GUI (Radial Menu - Qt-based)
pip install cyberclip[gui]

# With Web Interface (Flask-based)
pip install cyberclip[web]

# With all optional features
pip install cyberclip[all]
```

📖 **See [INSTALL.md](INSTALL.md) for detailed installation options and platform-specific notes.**

## With uv

```bash
# Basic installation
uv tool install git+https://github.com/BongoKnight/cyberclip

# With all features
uv tool install "git+https://github.com/BongoKnight/cyberclip[all]"

# For trying (temporary)
uv tool run git+https://github.com/BongoKnight/cyberclip

# Run
cyberclip
```

## With pipx

```bash
# Basic installation
pipx install "cyberclip @ git+https://github.com/BongoKnight/cyberclip"

# With all features
pipx install "cyberclip[all] @ git+https://github.com/BongoKnight/cyberclip"
```

## With Docker

```bash
git clone https://github.com/BongoKnight/cyberclip
cd cyberclip
docker build -t cyberclip .
docker run -d -p 8000:8000 cyberclip
```

# Generate documentation

```python
pip install mkdocs mkdocs-gen-files mkdocs-material mkdocs-autorefs mkdocstrings-python
mkdocs gh-deploy
```


# Thanks to and similar project:

- [Textual](https://textual.textualize.io/)
- [Textual-pandas](https://github.com/dannywade/textual-pandas)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [Visidata](https://www.visidata.org/)
- [Cheepy](https://github.com/securisec/chepy)
- [Cyberbro](https://github.com/stanfrbd/cyberbro)

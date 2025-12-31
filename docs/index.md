---
title: "Getting started"
---

# Installation

## Requirements

- Git
- Docker (for docker deployment)
- Python 3.12

## With uv (recommended)

```
# For trying
uv tool run git+https://github.com/BongoKnight/cyberclip

# For installation
uv tool install git+https://github.com/BongoKnight/cyberclip
cyberclip
```


## With pipx

```
python -m pip install pipx
python -m pipx install "cyberclip @ git+https://github.com/BongoKnight/cyberclip"
```

> You might need to use `python -m pipx ensurepath` in order to add the binary to your PATH. Sometimes pipx install is glitchy and thus not recommended.


## With Docker

```
git clone https://github.com/BongoKnight/cyberclip
cd cyberclip
docker build -t cyberclip .
docker run -d -p 8000:8000 cyberclip
```


- Create the .env file in `cyberclip` installation path

```bash
# If installed with uv, the default should be:
C:\Users\<user>\AppData\Roaming\uv\tools\cyberclip\Lib\site-packages\cyberclip
# If installed with pipx, the default should be:
C:\Users\<user>\pipx\venvs\cyberclip\Lib\site-packages\cyberclip
```

- Add customs parser/actions in the `private` directory under `cyberclip/userAction` and `cyberclip/userTypeParser`, some example will be added in the "Getting started" tutoriel and in the `graveyard` directory.

> If installed with pipx, the installation path should be something like `C:\Users\<user>\pipx\venvs\cyberclip\Lib\site-packages\cyberclip` (Windows) or `/home/<user>/.local/share/pipx/venvs/cyberclip/lib/python3.13/site-packages/cyberclip/` (Linux)

Then you should be able to run the script with :

```bash
# On linux
cyberclip
# On Windows
cyberclip.exe
# Or alternatively with :
cd "C:\Users\<user>\AppData\Local\Programs\Python\Python312\Lib\site-packages\cyberclip" && python3 app.py
```

# Requests and improvments

- Feel free to open an issue if you think of other type of data to parse, or if you think of an action you would like to be applied to a specific type of data,
- Feel free to open an issue if you have some crash, I think I need to improve the error handling to avoid the crashing of the GUI 
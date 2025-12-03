---
title: "Getting started"
---

# Installation

I only tested the installation using pipx :

```bash
# Windows users might need to specify the full python.exe path
python.exe -m pip install pipx
python.exe -m pipx install "cyberclip @ git+https://github.com/BongoKnight/cyberclip"
```

> You might need to use `python.exe -m pipx ensurepath` in order to add the binary to your PATH.

- Create the .env file in `cyberclip` installation path
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
---
title: "Getting started"
---

# Installation

```bash
# Windows users might need to specify the full python.exe path
python -m pip install "cyberclip @ git+https://github.com/BongoKnight/cyberclip"
```

- Create the config in `cyberclip/data/config.yml` from the `cyberclip/data/config.yml.bak`
- Add customs parser/actions in the `private` directory under `cyberclip/userAction` and `cyberclip/userTypeParser`, some example will be added in the "Getting started" tutoriel and in the `graveyard` directory.

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
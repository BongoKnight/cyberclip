# Installation

```bash
python -m pip install 'cyberclip @ git+https://github.com/BongoKnight/cyberclip'
```
- Create the config in `cyberclip/data/config.yml` from the `cyberclip/data/config.yml.bak`
- Add customs parser/actions in the `private` directory under `cyberclip/userAction` and `cyberclip/userTypeParser`, some example will be added in the "Getting started" tutoriel and in the `graveyard` directory.


# Use case

## Demo

![textual](https://user-images.githubusercontent.com/22347055/209771427-53017604-acfe-4543-9eb3-dad905229ce1.gif)

## Features

### Extract data
![datatype](https://user-images.githubusercontent.com/22347055/209772810-81ba33a0-aba8-40d7-9487-1790bed7a984.gif)

At the moment, these datatypes are handled :
- Text
- Url
- Domain
- TSV
- md5 and SHA1
- IP
- Autonomous system number
- Mail
- HTML
- Yara
- JSON
- Mitre TTP and Phones (need to be improved)

### Filter actions by name and type
![filter](https://user-images.githubusercontent.com/22347055/209774170-2f22c165-07a4-4134-a7e5-4ba044290b82.gif)

### Complex actions with auto-generated input
![modal](https://github.com/BongoKnight/cyberclip/assets/22347055/cb8ee6ae-301e-4c19-a070-b50296386102)

### Save data

Showed data can be exported to clipboard or to a file.

# To do

- [ ] Make the script installable with pip+git
- [ ] MKDocs on GitHub
- [x] Make a gitignore
- [x] Add an history (Undo et Redo buttons)
- [x] Add a command palette
- [x] Filtering of types :
	- [x] Button to filter actions per type
	- [x] Button to (un)select all types at once
- [ ] Write docs :
	- [ ] For users
	- [ ] For devs (how to write custom parsers/actions)
- [x] Add an help field to make a long description of action possible. (ie sort) 
	- [x] Use of  instance.execute/__str__.__doc__
- [x] Wrap custom actions and UserTypeParser in a `private` dir
- [x] As the view container is a Static, it could accept a renderable widget as action result... It might be a way to make scripts with more interractions :
	- [x] Action to render text as Markdown
	- [ ] Action to render table in DataTable widget (with custom action to copy colum or row)
	- [ ] Regex Highlight
	- [x] Code Highlight
- [ ] Write `public` actions :
	- [x] TSV to Markdown Table
	- [x] Domain and Url to base URL
	- [x] Domain to IP
	- [x] IP to ASN
	- [x] Extract elements from HTML
	- [ ] Markdown Table to TSV
	- [x] Mitre description
	- [x] Prepend per line
	- [x] Append per line
	- [x] Regex select or unselect
	- [ ] Regex Highlighter
	- [ ] Regex substitution
	- [x] Remove empty lines (Filter with [^.])
	- [x] Stats/Counts per lines
	- [x] Reverse sort 
	- [ ] Search in MISP
	- [x] Search in OpenCTI
	- [x] Search in Yeti
 	- [x] Add in Yeti 	
	- [x] Select top N lines
	- [x] URL open
	- [ ] Url redirect chain
	- [x] Url to Html
	- [x] HTML filtering with CSS selectors
	- [ ] JSON filtering with pyjq (installing not straightforward in Windows need to check for other options...)
- [ ] Custom parsers :
	- [x] For HTML
	- [x] For JSON
	- [x] For Yaml
	- [ ] For JWT
	- [ ] For lat long coordinates
	- [ ] For tabular data (CSV, TSV, Markdown)
		- [x] Import in pandas dataframe
			-[x] Ok for TSV
		- [ ] (WIP) Allow enrichment of dataframe (Another UI for entering the conf?) (and so of it's visual representation)
			- [ ] From SQLite
			- [ ] From CSV
			- [ ] From MISP
			- [ ] From SQLite
		- [x] Update sort action for DataFrame
		- [x] Write filter and stats action for DataFrame (possibility to open dataframe in visidata?)
	- [x] For AS Number
		- [ ] AS to Regex
		- [x] AS range
- [x] Make a domain and a host Parser, improve the domain parsing
- [ ] Assync action results
- [ ] Assync loading of action (some loading times are long, especially for AS action)
- [ ] Requirement.txt
- [ ] Save action with file input (need to implement modal, have to check textual discord).
- [ ] Write python script/template to generate custom Parser/Action

# Thanks to and similar project:

- [Textual](https://textual.textualize.io/)
- [Textual-pandas](https://github.com/dannywade/textual-pandas)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [Visidata](https://www.visidata.org/)
- [Cheepy](https://github.com/securisec/chepy)

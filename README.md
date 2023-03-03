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
- Mitre TTP and Phones (need to be improved)

### Filter actions by name and type
![filter](https://user-images.githubusercontent.com/22347055/209774170-2f22c165-07a4-4134-a7e5-4ba044290b82.gif)

### Save data

Showed data can be exported to clipboard or to a file.

# To do

- [x] Make a gitignore
- [x] Add an history (Undo et Redo buttons)
- [x] Filtering of types :
	- [x] Button to filter actions per type
	- [x] Button to (un)select all types at once
- [ ] Write docs :
	- [ ] For users
	- [ ] For devs (how to write custom parsers/actions)
- [ ] Add an help field to make a long description of action possible. (ie sort) 
	- [ ] Use of  instance.execute/__str__.__doc__
- [x] Wrap custom actions and UserTypeParser in a `private` dir
- [ ]
- [ ] Write `public` actions :
	- [x] TSV to Markdown Table
	- [x] Domain and Url to base URL
	- [x] Domain to IP
	- [x] IP to ASN
	- [x] Extract elements from HTML
	- [ ] Markdown Table to TSV
	- [x] Mitre description
	- [ ] Prepend per line
	- [ ] Regex Highlighter
	- [ ] Regex substitution
	- [x] Remove empty lines (Filter with [^.])
	- [x] Stats/Counts per lines
	- [x] Reverse sort 
	- [ ] Search in MISP
	- [x] Search in OpenCTI
	- [ ] Search in Yeti
	- [x] Select top N lines
	- [x] URL open
	- [ ] Url redirect
	- [x] Url to Html
	- [x] HTML filtering with CSS selectors
	- [ ] JSON filtering with pyjq
	- [ ] Code Highlight
- [ ] Custom parsers :
	- [x] For HTML
	- [ ] For JSON
	- [ ] For Yaml
	- [ ] For tabular data (CSV, TSV, Markdown)
		- [ ] Import in pandas dataframe
			-[ ] Ok for TSV
		- [ ] (WIP) Allow enrichment of dataframe (Another UI for entering the conf?) (and so of it's visual representation)
			- [ ] From SQLite
			- [ ] From CSV
			- [ ] From MISP
			- [ ] From SQLite
		- [ ] Update sort action for DataFrame
		- [ ] Write filter and stats action for DataFrame (possibility to open dataframe in visidata?)
	- [x] For AS Number
		- [ ] AS to Regex
		- [ ] AS range
- [x] Make a domain and a host Parser, improve the domain parsing
- [ ] Assync action results
- [ ] Requirement.txt
- [ ] Save action with file input (need to implement modal, have to check textual discord).
- [ ] Write python script/template to generate custom Parser/Action

# Thanks to and similar project:

- [Textual](https://textual.textualize.io/)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [Visidata](https://www.visidata.org/)
- [Cheepy](https://github.com/securisec/chepy)

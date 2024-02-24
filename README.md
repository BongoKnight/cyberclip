# Installation and documentation 

You may want to see some screens records, documentation or even a features tour, everything is available here :

[https://bongoknight.github.io/cyberclip/](https://bongoknight.github.io/cyberclip/)

# Screen recording

![textual](https://user-images.githubusercontent.com/22347055/209771427-53017604-acfe-4543-9eb3-dad905229ce1.gif)


# To do

- [x] Make the script installable with pip+git
- [x] MKDocs on GitHub
- [ ] Recipes panes :
	- [ ] Loading of all actions
	- [ ] Refactoring of actions options (complex_data)
- [x] Make a gitignore
- [x] Add an history (Undo et Redo buttons) :
	- [x] Now done in baseline Textarea
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
	- [x] Action to render table in DataTable widget (with custom action to copy colum or row)
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
	- [x] JSON filtering with pyjq (with jsonpath_ng, syntax is quite hard...)
- [ ] Custom parsers :
	- [x] For HTML
	- [x] For JSON
	- [x] For Yaml
	- [ ] For uuid
	- [ ] For JWT
	- [ ] For lat long coordinates (maybe as a tutorial)
	- [ ] For tabular data (CSV, TSV, Markdown)
		- [x] Import in pandas dataframe
			-[x] Ok for TSV
		- [x] (WIP) Allow enrichment of dataframe (Another UI for entering the conf?) (and so of it's visual representation)
			- [-] ~~From SQLite~~
			- [-] ~~From CSV~~
			- [-] ~~From MISP~~
			- [-] ~~From SQLite~~
			- [x] From action from command palette
		- [x] Update sort action for DataFrame
		- [x] Write filter and stats action for DataFrame
		- [ ] set first line as column name
	- [x] For AS Number
		- [ ] AS to Regex
		- [x] AS range
- [x] Make a domain and a host Parser, improve the domain parsing
- [ ] Assync action results
- [ ] Assync loading of action (some loading times are long, especially for AS action)
- [x] Requirement.txt
- [ ] Save action with file input (need to implement modal, have to check textual discord).
- [ ] Write python script/template to generate custom Parser/Action

# Thanks to and similar project:

- [Textual](https://textual.textualize.io/)
- [Textual-pandas](https://github.com/dannywade/textual-pandas)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [Visidata](https://www.visidata.org/)
- [Cheepy](https://github.com/securisec/chepy)

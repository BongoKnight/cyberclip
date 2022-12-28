# To do

- [x] Make a gitignore
- [ ] Add an help field to make a long description of action possible. (ie sort) 
	- [ ] Use of  instance.execute/__str__.__doc__
- [ ] Wrap custom actions and UserTypeParser in a `private` dir
- [ ] Write `public` actions :
	- [x] TSV to Markdown Table
	- [x] Domain and Url to base URL
	- [x] Domain to IP
	- [x] IP to ASN
	- [ ] Markdown Table to TSV
	- [ ] Mitre description
	- [ ] Prepend per line
	- [ ] Regex Highlighter
	- [ ] Regex substitution
	- [x] Remove empty lines (Filter with [^.])
	- [x] Stats/Counts per lines
	- [x] Reverse sort 
	- [ ] Search in MISP
	- [ ] Search in OpenCTI
	- [ ] Search in Yeti
	- [ ] Select top N lines
	- [x] URL open
	- [ ] Url redirect
	- [ ] Url to Html
	- [ ] Code Highlight
- [ ] Custom parsers :
	- [ ] For tabular data (CSV, TSV, Markdown)
		- [ ] Import in pandas dataframe
		- [ ] Connect with enrichment module
	- [ ] For AS Number
		- [ ] AS to Regex
		- [ ] AS range
- [ ] Make a domain and a host Parser, improve the domain parsing
- [ ] Assync action results
- [ ] Requirement.txt
- [ ] Save action with file input.
- [ ] Write python script/template to generate custom Parser/Action

# Thanks to and similar project:

- [Textual](https://textual.textualize.io/)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [Visidata](https://www.visidata.org/)
- [Cheepy](https://github.com/securisec/chepy)

try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from jsonpath_ng import jsonpath, parse
import yaml

class JSONExtractAction(actionInterface):
    """
A action module to extract data from an JSON.
Use jsonpath-ng module.

    """

    def __init__(self, parsers = {}, supportedType = {"json","yaml"}, complex_param={"Selectors":[]}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Extract from JSON/YAML with Path selector"
        self.results = {}

    def filter_json(self, json_objects: list[dict]):
        extract = {}
        if json_objects:
            for json in json_objects:
                for selector in self.complex_param.get("Selectors",[]):
                    try:
                        extract.update({selector:[match.value for match in parse(selector).find(json) if match.value]})
                    except:
                        pass
                self.results.update({str(json):extract})
        return extract
        
    def execute(self) -> object:
        """Execute the action."""
        self.results = {}
        self.observables = self.get_observables()
        if self.observables.get("json"):
            json_objects = self.observables.get("json")
            self.filter_json(json_objects)          
        if self.observables.get("yaml"):
            json_objects = self.observables.get("yaml")
            self.filter_json(json_objects)        
        return self.results
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        filtered_jsons = self.execute()
        
        for json_objects, extract in filtered_jsons.items():
            constant_length = True if len(set([len(values) for values in extract.values()])) == 1 else False
            if not constant_length:
                for selector, values in extract.items():
                    newline = "\r\n"
                    lines.append(f"{selector}\r\n{newline.join([str(i) for i in values ])}")
            else:
                lines.append("\t".join([selector for selector in extract.keys()]))
                zipped_extract = zip(*[values for values in extract.values()])
                lines+= ["\t".join([str(i) for i in tupple]) for tupple in zipped_extract]

        return  "\r\n".join(lines)

if __name__=='__main__':
    from userTypeParser.JsonParser import JSONParser
    data = '[{"a":"toto"},{"a":"titi"}]'
    #data =  '{"a":"1"}'
    text_parser = JSONParser(data)
    a = str(JSONExtractAction({"json":text_parser},["json"], complex_param={"Selectors":["[*].a"]}))
    print(f"JSON: {text_parser.extract()}", f"Extract : {a}")
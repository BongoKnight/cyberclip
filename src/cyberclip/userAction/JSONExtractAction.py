try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from jsonpath import jsonpath
import json
import yaml

class JSONExtractAction(actionInterface):
    """
A action module to extract data from an JSON.
Use jsonpath module.

    """

    def __init__(self, parsers = {}, supportedType = {"json","yaml"}, complex_param={"Selectors":[]}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Extract from JSON/YAML with Path selector"
        self.results = {}

    def filter_json(self, json_objects: str):
        if json_objects:
            for json_str in json_objects:
                extract = {}
                for selector in self.get_value("Selectors"):
                    try:
                        extract[selector] = jsonpath(json.loads(json_str), selector)
                    except Exception as e:
                        extract[selector] = [f"Error : {e}"]
            self.results.update({str(json_str):extract})
        return self.results
        
    def execute(self) -> object:
        """Execute the action."""
        self.results = {}
        self.observables = self.get_observables()
        if self.observables.get("json"):
            json_objects = self.observables.get("json")
            self.filter_json(json_objects)          
        if self.observables.get("yaml"):
            json_objects = [json.dumps(yaml.safe_load(yaml_str)) for yaml_str in self.observables.get("yaml")]
            self.filter_json(json_objects)        
        return self.results
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        filtered_jsons = self.execute()
        for json_objects, extract in filtered_jsons.items():
            for selector, value in extract.items():
                lines.append(f"{selector}\t{str(value)}")
        return  "\r\n".join(lines)

if __name__=='__main__':
    from userTypeParser.JsonParser import JSONParser
    data = '[{"a":"toto"},{"a":"titi"}]'
    #data =  '{"a":"1"}'
    text_parser = JSONParser(data)
    a = str(JSONExtractAction({"json":text_parser},["json"], complex_param={"Selectors":["[*].a"]}))
    print(f"JSON: {text_parser.extract()}", f"Extract : {a}")
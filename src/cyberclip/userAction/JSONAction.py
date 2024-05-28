try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from jsonpath import jsonpath
import json
from json import dumps, loads
import yaml
import pandas as pd

# Thanks too https://github.com/ScriptSmith/socialreaper/blob/master/socialreaper/tools.py#L8
from collections.abc import MutableMapping
def flatten(dictionary, parent_key=False, separator='.'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            if not value.items():
                items.append((new_key,None))
            else:
                items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            if len(value):
                for k, v in enumerate(value):
                    items.extend(flatten({str(k): v}, new_key, separator).items())
            else:
                items.append((new_key,None))
        else:
            items.append((new_key, value))
    return dict(items)

class JSONExtractAction(actionInterface):
    """A action module to extract data from a JSON object.  
    Use jsonpath module.
    """
    CONF = {"Selectors":{"type":"tags", "value":""}, "Extract as TSV":{"type":"bool","value":"True"}}
    def __init__(self, parsers = {}, supportedType = {"json","yaml"}, complex_param=CONF):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Extract from JSON/YAML with Path Selector"
        self.results = {}

    def filter_json(self, json_objects: str):
        if json_objects:
            for json_str in json_objects:
                extract = {}
                for selector in self.get_param_value("Selectors"):
                    try:
                        extract[selector] = jsonpath(loads(json_str), selector)
                    except Exception as e:
                        extract[selector] = [f"Error : {e}"]
            self.results.update({str(json_str):extract})
        return self.results
        
    def execute(self) -> object:
        self.results = []
        self.observables = self.get_observables()
        if json_objects:=self.observables.get("json"):
            for json in json_objects:
                self.filter_json(json)          
        if self.observables.get("yaml") and not self.observables.get("json"):
            json_objects = [dumps(yaml.safe_load(yaml_str)) for yaml_str in self.observables.get("yaml")]
            for json in json_objects:
                self.filter_json(json)    
        return self.results
    
    def __str__(self):
        filtered_jsons = self.execute()
        df = pd.DataFrame(filtered_jsons)
        return df.to_csv(sep="\t")


class JSONFlattenAction(actionInterface):
    """A action module to flatten data from a JSON object.  
    Use jsonpath module.
    """

    def __init__(self, parsers = {}, supportedType = {"json","yaml"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Flatten JSON/YAML"
        self.results = {}
        
    def execute(self) -> object:
        self.results = {}
        self.observables = self.get_observables()
        json_objects = {}
        if self.observables.get("json"):
            json_objects = [loads(json) for json in self.observables.get("json")]
        if self.observables.get("yaml") and not self.observables.get("json"):
            json_objects = [yaml.safe_load(yaml_str) for yaml_str in self.observables.get("yaml")]
        for json in json_objects:
            self.results[str(json)] = flatten(json)
        return self.results
    
    def __str__(self):
        self.execute()
        return  "\n".join([str(json_object) for json_object in self.results.values()])



if __name__=='__main__':
    from userTypeParser.JsonParser import JSONParser
    data = '[{"a":"toto"},{"a":"titi"}]'
    #data =  '{"a":"1"}'
    text_parser = JSONParser(data)
    a = str(JSONExtractAction({"json":text_parser},["json"], complex_param={"Selectors":["[*].a"]}))
    print(f"JSON: {text_parser.extract()}", f"Extract : {a}")
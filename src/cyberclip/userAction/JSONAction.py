try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import jq
import json 
import yaml
import pandas as pd

# Thanks to https://github.com/ScriptSmith/socialreaper/blob/master/socialreaper/tools.py#L8
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
    """Extract data from a JSON or YAML object using jq. You can test your queries here: https://jqplay.org/

Example::

```json
{"a":"elem1","b":"elem2","c":3, "d":[{"a":"elem3","b":"elem4","c":5},{"a":"elem5","b":"elem6","c":2}]}
```

With the JSON above: 

- `.a` selector will return `"elem1"`
- `.c` selector  will return `3`
- `.d[].a` selector will return `"elem3"\n"elem5"`
- `.d[] | select(.c>2)` selector will return `{"a": "elem3","b": "elem4","c": 5}`

    """
    CONF = {"Selectors":{"type":"json", "value":[]}, "Get only values":{"type":"bool","value": True}}
    def __init__(self, parsers = {}, supportedType = {"json","yaml"}, complex_param=CONF):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Extract from JSON/YAML with Path Selector"
        self.results : dict[str, dict] = {}
        self.observables: dict[str, dict] = {}

    def filter_json(self, json_str: str):
        if json_str:
            extract = {}
            data = json.loads(json_str)
            for selector in self.get_param_value("Selectors"):
                try:
                    extract[selector] = jq.compile(selector).input_value(data).text()
                    actual_value = self.results.get(json_str, {})
                    actual_value.update({selector:extract[selector]})
                    self.results[json_str] = actual_value
                except Exception as e:
                    extract[selector] = [f"Error : {e}"]
                # if len(set([len(extracted) for selector, extracted in extract.items()])) == 1:
                #     atomic_dict = [{k: v[i] for k, v in extract.items()} for i in range(len(next(iter(extract.values()))))]
                #     #atomic_dict = {i: [v[i] for k, v in extract.items()] for i in range(len(next(iter(extract.values()))))}
                #     #atomic_dict = [[v[i] for k, v in extract.items()] for i in range(len(next(iter(extract.values()))))]
                #     self.results.update({json_str:atomic_dict})
                # else:
                #     self.results.update({json_str:[extract]})

        return self.results
        
    def execute(self) -> object:
        self.results = []
        self.observables = self.get_observables()
        if json_objects:=self.observables.get("json"):
            for _json in json_objects:
                self.filter_json(_json)          
        if self.observables.get("yaml") and not self.observables.get("json"):
            json_objects = [json.dumps(yaml.safe_load(yaml_str)) for yaml_str in self.observables.get("yaml")]
            for _json in json_objects:
                self.filter_json(_json)    
        return self.results
    
    def __str__(self):
        self.execute()
        text = []
        if self.get_param_value("Get only values"):
            for _json, extract in self.results.items():
                for value in extract.values():
                    text.append(str(value))
        else:
            for k,v in self.results.items():
                text.append(f"{k}\t{json.dumps(v,indent=None)}")
        return "\n".join(text)


class JSONSchemeAction(actionInterface):
    """Display the scheme of a JSON object.

Example::

```json
{"a":"elem1","b":"elem2","c":3, "d":[{"a":"elem3","b":"elem4","c":5},{"a":"elem5","b":"elem6","c":2}]}
```

With the JSON above returns:

```
a
b
c
d
d[]
d[].a
d[].b
d[].c
```
    """
    def __init__(self, parsers = {}, supportedType = {"json","yaml"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Show JSON/YAML scheme"
        self.json_paths = set()

    def get_json_paths(self, data, current_path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                self.json_paths.add(new_path)
                self.get_json_paths(value, new_path)

        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_path = f"{current_path}[]"
                self.json_paths.add(new_path)
                self.get_json_paths(item, new_path)
        else:
            # For primitive values, print the current path
            self.json_paths.add(current_path)


        
    def execute(self) -> set:
        self.json_paths = set()
        self.observables = self.get_observables()
        if json_objects:=self.observables.get("json"):
            for _json in json_objects:
                self.get_json_paths(json.loads(_json))          
        if self.observables.get("yaml") and not self.observables.get("json"):
            json_objects = [json.dumps(yaml.safe_load(yaml_str)) for yaml_str in self.observables.get("yaml")]
            for _json in json_objects:
                self.get_json_paths(_json)    
        return self.json_paths
    
    def __str__(self):
        return "\r\n".join(list(self.execute()))







class JSONFlattenAction(actionInterface):
    """A action module to flatten data from a JSON object.  
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
            json_objects = [json.loads(json) for json in self.observables.get("json")]
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
    data = '{"a":"toto","b":"tutu","c":"unique", "d":[{"a":"titi","b":"tutu"},{"a":"toti","b":"tati"}]}'
    #data =  '{"a":"1"}'
    text_parser = JSONParser(data)
    d = str(JSONExtractAction({"json":text_parser},["json"],complex_param={"Selectors":{"type":"tags", "value":[".a"]}}))
    c = str(JSONSchemeAction({"json":text_parser},["json"]))
    print(f"Scheme:{c}")
    print(f"Extract: {d}")
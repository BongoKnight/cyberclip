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


class JSONExtractActionv2(actionInterface):
    r"""Extract data from JSON or YAML using jq selectors while preserving hierarchy.

    Uses jq-style selectors to extract specific fields from JSON/YAML data while
    maintaining the original nested structure. Creates a pruned copy that contains
    only the selected paths.

    Supported Types:
        json, yaml

    Parameters:
        Selectors (json): List of jq-style path selectors to extract.
            Examples: ".a", ".d[].a", ".[] | select(.c>2)"
            Default: []
        Get only values (bool): If True, return only scalar values extracted.
            If False, return the full pruned JSON structure.
            Default: True

    Example:
        >>> from userTypeParser.JsonParser import JSONParser
        >>> data = '{"a":"elem1","b":"elem2","c":3,"d":[{"a":"elem3","c":5}]}'
        >>> parser = JSONParser(data)
        >>> action = JSONExtractActionv2({"json": parser})
        >>> action.complex_param["Selectors"]["value"] = [".a", ".d[].a"]
        >>> print(action)
        elem1
        elem3

    Note:
        Test selectors at https://jqplay.org/
    """

    CONF = {"Selectors": {"type": "json", "value": []},
            "Get only values": {"type": "bool", "value": True}}

    def __init__(self, parsers = {}, supportedType = {"json","yaml"}, complex_param=CONF):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Extract from JSON/YAML with Path Selector (hierarchy preserved)"
        self.results: dict[str, object] = {}
        self.observables: dict[str, dict] = {}

    # --- internal helpers ---

    @staticmethod
    def _get_at_path(data, path):
        cur = data
        for key in path:
            cur = cur[key]
        return cur

    @staticmethod
    def _assign(container, path, value):
        """Return a container with value assigned at path, creating intermediate nodes.
           - Dict keys for string keys
           - Lists for integer indices (preserving indices with None placeholders)
        """
        if not path:
            return value
        key, rest = path[0], path[1:]

        if isinstance(key, int):
            # Ensure list container
            if container is None or not isinstance(container, list):
                container = []
            # Ensure size
            while len(container) <= key:
                container.append(None)
            container[key] = JSONExtractActionv2._assign(container[key], rest, value)
            return container
        else:
            # Ensure dict container
            if container is None or not isinstance(container, dict):
                container = {}
            container[key] = JSONExtractActionv2._assign(container.get(key), rest, value)
            return container

    @staticmethod
    def _iter_scalar_values(obj):
        """Yield all scalar (non-dict, non-list) values from nested structure."""
        if isinstance(obj, dict):
            for v in obj.values():
                yield from JSONExtractActionv2._iter_scalar_values(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from JSONExtractActionv2._iter_scalar_values(v)
        else:
            yield obj

    # --- core extraction ---

    def filter_json(self, json_str: str):
        if not json_str:
            return self.results

        try:
            data = json.loads(json_str)
        except Exception as e:
            # Keep a trace of error per input
            self.results[json_str] = {"error": f"Invalid JSON: {e}"}
            return self.results

        selectors = self.get_param_value("Selectors") or []
        pruned = None  # let _assign decide root type if needed

        for selector in selectors:
            try:
                # Get all paths for the selector, e.g., ["a","b",0,"c"]
                paths = jq.compile(f'path({selector})').input_value(data).all()
            except Exception as e:
                # Record selector error but continue others
                pruned = pruned or {}
                sel_errs = pruned.setdefault("_selector_errors", [])
                sel_errs.append({selector: f"{e}"})
                continue

            # For each concrete path, copy the value and rebuild structure
            for p in paths:
                try:
                    value = self._get_at_path(data, p)
                    pruned = self._assign(pruned, p, value)
                except Exception as e:
                    pruned = pruned or {}
                    sel_errs = pruned.setdefault("_selector_errors", [])
                    sel_errs.append({selector: f"{e}"})

        # If nothing matched, default to empty dict
        self.results[json_str] = pruned if pruned is not None else {}
        return self.results

    def execute(self) -> object:
        """Execute jq extraction on all parsed JSON/YAML observables.

        Applies all configured selectors to each JSON/YAML object and builds
        pruned structures containing only selected paths.

        Returns:
            dict[str, Any]: Keys are original JSON/YAML strings, values are
                pruned structures or error dicts.
        """
        self.results = {}
        self.observables = self.get_observables()

        if json_objects := self.observables.get("json"):
            for _json in json_objects:
                self.filter_json(_json)

        # If only YAML is present, parse to JSON strings and process
        if self.observables.get("yaml") and not self.observables.get("json"):
            json_objects = []
            for yaml_str in self.observables.get("yaml"):
                try:
                    parsed = yaml.safe_load(yaml_str)
                    json_objects.append(json.dumps(parsed))
                except Exception as e:
                    self.results[yaml_str] = {"error": f"Invalid YAML: {e}"}
            for _json in json_objects:
                self.filter_json(_json)

        return self.results

    def __str__(self):
        """Return human-readable representation of extracted data.

        Calls :meth:`execute` and formats output based on "Get only values" parameter.

        Returns:
            str: Either scalar values (one per line) or formatted JSON structures.
        """
        self.execute()
        text = []
        only_values = self.get_param_value("Get only values")

        if only_values:
            # Print only scalar values extracted from the pruned structures
            for _json, pruned in self.results.items():
                for v in self._iter_scalar_values(pruned):
                    text.append(str(v))
        else:
            # Print original input + its pruned JSON, grouped by prefixes (hierarchy preserved)
            for k, v in self.results.items():
                try:
                    text.append(f"{json.dumps(v, ensure_ascii=False, indent=2)}")
                except Exception:
                    # Fallback if non-serializable values sneak in
                    text.append(f"{k}\t{str(v)}")

        return "\n".join(text)

class JSONBeautifierAction(actionInterface):
    r"""Format JSON with indentation for readability.

    Pretty-prints JSON objects with 4-space indentation.

    Supported Types:
        json

    Example:
        >>> from userTypeParser.JsonParser import JSONParser
        >>> data = '{"a":"elem1","b":"elem2","c":3}'
        >>> parser = JSONParser(data)
        >>> action = JSONBeautifierAction({"json": parser})
        >>> print(action)
        {
            "a": "elem1",
            "b": "elem2",
            "c": 3
        }
    """
    def __init__(self, parsers = {}, supportedType = {"json"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = 'Pretty print JSON'
        self.results = {}

    def execute(self) -> dict[str, dict]:
        """Execute beautification on all parsed JSON observables.

        Returns:
            dict[str, dict]: Parsed JSON objects ready for pretty-printing.
        """
        self.observables = self.get_observables()
        self.results = self.observables.get("json")

    def __str__(self):
        """Return human-readable representation of beautified JSON.

        Calls :meth:`execute` and formats output with 4-space indentation.

        Returns:
            str: Formatted JSON with indentation.
        """
        self.execute()
        if len(self.results) == 1:
            return json.dumps(json.loads(self.results[0]),indent=4)
        else:
            return json.dumps(json.loads(self.results),indent=4)

class JSONExtractAction(actionInterface):
    r"""Extract data from JSON or YAML using jq selectors.

    Uses jq-style selectors to extract and filter fields from JSON/YAML data.
    Results are flattened rather than preserving hierarchy (see JSONExtractActionv2
    for hierarchy-preserving extraction).

    Supported Types:
        json, yaml

    Parameters:
        Selectors (json): List of jq-style path selectors to extract.
            Examples: ".a", ".d[].a", ".[] | select(.c>2)"
            Default: []
        Get only values (bool): If True, return only extracted values.
            If False, return selector-to-value mappings per input.
            Default: True

    Example:
        >>> from userTypeParser.JsonParser import JSONParser
        >>> data = '{"a":"elem1","b":"elem2","c":3,"d":[{"a":"elem3","c":5},{"a":"elem5","c":2}]}'
        >>> parser = JSONParser(data)
        >>> action = JSONExtractAction({"json": parser})
        >>> action.complex_param["Selectors"]["value"] = [".a", ".d[].a"]
        >>> print(action)
        elem1
        elem3
        elem5

    Selector Examples:
        - ``.a`` returns ``"elem1"``
        - ``.c`` returns ``3``
        - ``.d[].a`` returns ``"elem3"`` and ``"elem5"``
        - ``.d[] | select(.c>2)`` returns ``{"a": "elem3", "c": 5}``

    Note:
        Test selectors at https://jqplay.org/
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
        """Execute jq extraction on all parsed JSON/YAML observables.

        Applies all configured selectors to each JSON/YAML object and stores
        extracted values keyed by selector.

        Returns:
            dict[str, dict[str, str]]: Keys are original JSON/YAML strings,
                values are dicts mapping selectors to their extracted values.
        """
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
        """Return human-readable representation of extracted data.

        Calls :meth:`execute` and formats output based on "Get only values" parameter.

        Returns:
            str: Either extracted values (one per line) or TSV of input and
                selector-to-value mappings.
        """
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
    r"""Display the structural schema of JSON or YAML data.

    Recursively traverses JSON/YAML structure and outputs all available paths
    in jq-style notation. Useful for discovering which selectors to use with
    JSONExtractAction.

    Supported Types:
        json, yaml

    Example:
        >>> from userTypeParser.JsonParser import JSONParser
        >>> data = '{"a":"elem1","b":"elem2","c":3,"d":[{"a":"elem3","c":5}]}'
        >>> parser = JSONParser(data)
        >>> action = JSONSchemeAction({"json": parser})
        >>> print(action)
        a
        b
        c
        d
        d[]
        d[].a
        d[].c
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
        """Execute schema extraction on all parsed JSON/YAML observables.

        Recursively walks all structures and collects all available paths.

        Returns:
            set[str]: Set of all unique path strings in jq-style notation.
        """
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
        """Return human-readable representation of JSON schema.

        Calls :meth:`execute` and formats output as one path per line.

        Returns:
            str: All discovered paths, one per line.
        """
        return "\r\n".join(list(self.execute()))







class JSONFlattenAction(actionInterface):
    r"""Flatten nested JSON or YAML into dot-notation key-value pairs.

    Converts nested dictionaries and arrays into a single-level dictionary where
    keys use dot notation to represent the original hierarchy (e.g., "a.b.0.c").

    Supported Types:
        json, yaml

    Example:
        >>> from userTypeParser.JsonParser import JSONParser
        >>> data = '{"a":"elem1","b":{"c":"elem2","d":3},"e":[1,2,3]}'
        >>> parser = JSONParser(data)
        >>> action = JSONFlattenAction({"json": parser})
        >>> print(action)
        {'a': 'elem1', 'b.c': 'elem2', 'b.d': 3, 'e.0': 1, 'e.1': 2, 'e.2': 3}
    """

    def __init__(self, parsers = {}, supportedType = {"json","yaml"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Flatten JSON/YAML"
        self.results = {}
        
    def execute(self) -> object:
        """Execute flattening on all parsed JSON/YAML observables.

        Applies recursive flattening to convert nested structures to
        dot-notation dictionaries.

        Returns:
            dict[str, dict]: Keys are original JSON/YAML strings, values are
                flattened dictionaries with dot-notation keys.
        """
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
        """Return human-readable representation of flattened JSON.

        Calls :meth:`execute` and formats output as Python dictionaries.

        Returns:
            str: Flattened dictionaries, one per line.
        """
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
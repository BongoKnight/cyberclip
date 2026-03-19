import os
import sys
import re
from dotenv import dotenv_values
from pathlib import Path
script_dir = os.path.dirname( __file__ )
parser_dir = os.path.join( script_dir, '..')
sys.path.append( parser_dir )
from userTypeParser.ParserInterface import ParserInterface

"""Interface for action module."""

class actionInterface():
    """Action Interface defines the minimum functions a parser needs to implement.

    - `execute` : The logic part of the action, this method define what the action does. 
    - `__str__` : Visual representation of the action after being executed.

    Attributes:
        parsers (dict of str:ParserInterface): A dict of parsers interface, these are used to 
            extract observales from text
        observables (list of str): A list of observables extracted by the parsers
        conf (dict): A configuration extracted from `conf.yaml`, this store data needed 
            for the action to be executed (API Key for example) 
        supportedType (list of str):  A list of type defined in the varaible `parsertype` 
            that are supported by the current action.
        results (list of object): Storing the result of the action execution

    Note:
        While overwriting `execute` method in a class which inherits from `ActionInterface`,
        you should modify the `results` attributes in order to return a dictionnary where
        keys are the parsed observable and values are the results of the action.

    Alternative Initialization:
        Actions can also declare defaults using class kwargs::

            class MyAction(actionInterface,
                           description="My Action",
                           supportedType={"ip"},
                           indicators="🔑"):
                pass

    """

    def __init__(self, **kwargs):
        """Initialize the action interface.

        Args:
            complex_param (dict[str, dict]): Configuration parameters for the action.
                Each key is a parameter name, each value is a dict with schema:

                - ``type`` (str): Parameter widget type. One of: "text", "bool",
                  "tags", "list", "fixedlist", "json", "longtext", "save".
                - ``value`` (Any): Default value matching the type.
                - ``choices`` (list, optional): For "list" and "fixedlist" types.

                See docs/Reference.md for detailed type documentation.

            parsers (dict[str, ParserInterface]): Injected parsers keyed by type.
            supportedType (set[str]): Parser types this action works with
                (e.g., {"ip", "domain"}). Only parsers matching these types
                will be available in ``self.parsers``.
            description (str): Short action name shown in TUI button.
            indicators (str): Emoji flags indicating action requirements:

                - 🔑 Requires API key in ``.env``
                - 📑 Requires external data file
                - 🌍 Makes network requests
                - 🚩 Potentially dangerous operation
                - 🐌 Slow operation

            conf (dict): Loaded configuration from ``.env`` file.
        """
        self.supportedType : set[str] = set()
        self.parsers : dict[str,ParserInterface] = {}
        self.complex_param : dict[str,dict] = {}
        for k, v in kwargs.items():
            setattr(self, k, v)


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        allowed_params = {"description":"", "supportedType":[], "indicators":"", "complex_param":{}, "conf":{}, "parsers":{}}
        for param in allowed_params:
            setattr(cls, param, kwargs.get(param, allowed_params[param]))

    
    def load_conf(self, conf_name, path='../.env'):
        conf = {}
        try:
            env = dotenv_values(Path(__file__).parent / path)
            for key, value in env.items():
                if key.lower().startswith(conf_name.lower()):
                    key_name = re.sub(f"^{conf_name.lower()}_","",key.lower()).lower()
                    conf[key_name]=value
            self.conf = dict(conf)
        except Exception as e:
            print("Error while loading config from .env")
        return self.conf
    
    def get_observables(self) -> dict[str,dict]:
        """
        Returns:
            self.observables (dict): Populate the `self.observables` by a dictionnary with the following structure :  
                {`<Parser_type>`:[`<list of observables of this type>`]}  
                Reset the `self.results` variables.

        Info:
            This method is implemented to simplify the writting of new action. If you want to differientiate how an action handle different type of observables (ie IP addresses and domain), you might use something like this in your `execute` method :  
            ```python
            self.observables = self.get_observables()
            for ip in self.observables.get("ip", []):
                <behaviour regarding IP address>
            for ip in self.observables.get("domain", []):
                <behaviour regarding Domain Name>
            ``` 
        """
        self.observables = {}
        self.results = {}
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.observables[parser.parsertype] = parser.extract()
        return self.observables
    
    def get_param_value(self, config_name) -> str:
        config = self.complex_param.get(config_name)
        if isinstance(config, dict):
            return config.get("value","")
        elif isinstance(config, str):
            return config
        else:
            return ""
        

    def execute(self) -> dict[str,dict]:
        """Execute the action
        
        Returns:
            results (dict): Returns a dictionary consisting of the observables
                parsed in text and the results of the action for each one of it. 

        Note:
            Values of the returned dict could be wathever you need. The key of the dict are used to make join
            between dataset in the table view of the TUI. 
        """
        return self.results

    def __str__(self):
        """Return a textual representation of the action results. By default returns
        the `str` representation of `self.results`. However you could make some pretty printing here, 
        such as Markdown, TSV or any other string representation that fulfill your needs.

        Note:
            This textual representation is displayed in the Terminal User Interface (TUI) when you execute the action. 
            This method is used to provides feedback. 
        """
        return str(self.execute())
    

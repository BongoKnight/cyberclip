import os
import sys
import yaml
import copy
from yaml.loader import SafeLoader
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
        parsers (list of ParserInterface): A list of parsers interface, these are used to 
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

    """
    
    def __init__(self, parsers: list[ParserInterface] = {}, supportedType: list[str] = {}, complex_param: dict = {}):
        """
        Args: 
            complex_param (dict): A dictionnary of value needed for executing the action properly typically a filename, config options, users choices, etc... This parameter is parsed by  
        """
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Quick description of the action."
        self.complex_param = complex_param
        self.observables = {}
        self.results = {}
        self.conf = {}
    
    def load_conf(self, conf_name, path='../data/conf.yml'):
        conf = {}
        try:
            with open(Path(__file__).parent / path, encoding="utf8") as f:
                self.config = yaml.load(f, Loader=SafeLoader)
                if self.config and self.config.get(conf_name):
                    for i in self.config.get(conf_name, {}):
                        if isinstance(i,dict):
                            for key, value in i.items():
                                conf.update({key:value})
                    self.conf = dict(conf)
        except Exception as e:
            print("Error while loading conf.yaml.")
        return self.conf
    
    def get_observables(self) -> dict:
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
                self.observables[parser.parsertype]=parser.extract()
        return self.observables
    
    def get_param_value(self, config_name):
        config = self.complex_param.get(config_name)
        if isinstance(config, dict):
            return config.get("value","")
        elif isinstance(config, str):
            return config
        else:
            return ""
        

    def execute(self) -> dict:
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
    

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
    """Parser Interface defines the minimum functions a parser needs to implement."""
    
    def __init__(self, parsers = {}, supportedType = {}, param_data : str = "", complex_param : dict = {}):
        """
        parsers is a list of objects that implements ParserInterface.
        supportedType is a list of type defined in the varaible `parsertype` that are supported by the current action.
        param is a small textual parameter typically to pass to a simple script which is not mandatory, such as flags.
        complex_param are used to generate a TUI to ask for them or can be entered as is, typically for file name, config, etc... 
        """
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Quick description of the action."
        self.param = param_data
        self.complex_param = complex_param
        self.complex_param_scheme = copy.deepcopy(complex_param)
        self.observables = {}
        self.results = {}
        self.conf = {}
        
    def execute(self) -> dict:
        """Execute the action
        
        Return a dict of matches and values.
        """
        return {}
    
    def load_conf(self, conf_name, path='../../data/conf.yml'):
        with open(Path(__file__).parent / path, encoding="utf8") as f:
            self.config = yaml.load(f, Loader=SafeLoader)
            if self.config.get(conf_name):
                conf = {}
                for i in self.config.get(conf_name):
                    if isinstance(i,dict):
                        for key, value in i.items():
                            conf.update({key:value})
                self.conf = dict(conf)
    
    def get_observables(self) -> dict:
        """
        Populate the observables with a dict of this form :
            <Parser_type>:[<list of observables of this type>]
        Reset the results variables.
        """
        self.observables = {}
        self.results = {}
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.observables[parser.parsertype]=parser.extract()
        return self.observables

    def __str__(self):
        """Visual representation of the action"""
        return self.execute()
    



import os
import sys
script_dir = os.path.dirname( __file__ )
parser_dir = os.path.join( script_dir, '..')
sys.path.append( parser_dir )
from userTypeParser.ParserInterface import ParserInterface

"""Interface for action module."""

class actionInterface():
    """Parser Interface defines the minimum functions a parser needs to implement."""
    
    def __init__(self, parsers={},supportedType= {}, param_data: str =""):
        """
        parsers is a list of objects that implements ParserInterface.
        supportedType is a list of type defined in the varaible `parsertype` that are supported by the current action.
        """
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Quick description of the action."
        self.param = param_data
        
    def execute(self) -> dict:
        """Execute the action
        
        Return a dict of matches and values.
        """
        return {}
    
    def __str__(self):
        """Visual representation of the action"""
        return self.execute()
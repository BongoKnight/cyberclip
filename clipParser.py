# -*- coding: utf-8 -*-

from inspect import getmembers, isfunction, isclass, ismodule, iscode
import userTypeParser
import userAction
from userAction.actionInterface import actionInterface
import os
import logging
from pathlib import Path

        
class clipParser():
    
    def __init__(self):
        self.actions = dict()
        self.parsers = dict()
        self.data = ""
        logging.basicConfig(filename="log.log")
        self.log = logging.Logger("DataParser")
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)
        # create formatter
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        
        # add formatter to ch
        self.ch.setFormatter(self.formatter)
        self.log.addHandler(self.ch)
        self.parserModuleImport = self.loadParser()
        self.actionModuleImport = self.loadAction()
        self.results = {}

        
    
    
    def loadParser(self):
        """
        Load all Parser defined in `userTypeParser` directory.
    
        Returns
        -------
         __import__('userTypeParser',fromlist=parserModules)
    
        """
        parserModules = []
        files = os.listdir(userTypeParser.__path__[0])
        for file in files :
            if file.endswith(".py") and file != "__init__.py":
                parserModuleName = file.split(".")[0]
                parserModules.append(parserModuleName)
                self.log.debug("Importing {} parser".format(parserModuleName))
        # import all parser parserModule
        parserModuleImport = __import__('userTypeParser',fromlist=parserModules)
        return parserModuleImport

    def loadAction(self):
        """
        Load all actions defined in `action` directory.
    
        Returns
        -------
        __import__('userAction',fromlist=actionModules)    
        """
        actionModules = []
        files = os.listdir(userAction.__path__[0])
        for file in files :
            if file.endswith(".py") and file != "__init__.py":
                actionModule = file.split(".")[0]
                actionModules.append(actionModule)
                self.log.debug("Importing {} parser".format(actionModule))
        # import all parser parserModule
        actionModuleImport = __import__('userAction',fromlist=actionModules)
        return actionModuleImport
        
    
    def parseData(self, data):
        """
        Handle textual datas and return a dict containing matches and type of data detected.
    
        Returns
        -------
         {"matches" : matches, "detectedType" : detectedType}
    
        """
        self.data = data
        self.parsers = dict()
        self.actions = dict()
        matches = {}
        detectedType = []

        # Load all parsers
        parserModules = dict((name, m) for name, m
                           in getmembers(self.parserModuleImport, ismodule))

        for parserModule in parserModules.keys():
            classes = dict((name, c) for name, c 
                           in getmembers(parserModules[parserModule], isclass))
            for className in classes.keys():
                if "Parser" in className:
                    instance = classes[className](data)
                    if instance.contains():
                        matches.update({instance.parsertype: instance.extract()})
                        # Adding parser in a dict of all parsers relative to the input
                        self.parsers.update({instance.parsertype:instance})
                        self.log.debug("Paste contains {}".format(instance.parsertype))
                        detectedType.append(instance.parsertype)

        # Load all actions
        actionModules = dict((name, m) for name, m
                    in getmembers(self.actionModuleImport, ismodule))

        for actionModule in actionModules.keys():
            classes = dict((name, c) for name, c 
                           in getmembers(actionModules[actionModule], isclass))
            for className in classes.keys():
                if "Action" in className:
                    instance = classes[className](self.parsers)
                    if hasattr(instance, "description"):
                        # Adding action in a dict of all parsers relative to the input
                        self.actions.update({instance.description : instance})
                        self.log.debug("Paste contains {}".format(instance.description))

        self.results = {"matches" : matches, "detectedType" : detectedType, "actions": self.actions, "parsers":self.parsers}
        return self.results
if __name__=='__main__':
    a = clipParser()
    data = "127.0.0.1, 124.0.12.23 SARA-65890 simon@vade.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    print(a.parseData(data))
    for action in a.actions:
        print(action) 
        print(a.actions.get("Extract all elements."))



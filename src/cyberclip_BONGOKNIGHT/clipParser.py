# -*- coding: utf-8 -*-

from inspect import getmembers, isfunction, isclass, ismodule, iscode
import userTypeParser
import userTypeParser.private

import userAction
import userAction.private

import os
import logging
from pathlib import Path

        
class clipParser():
    
    def __init__(self):
        self.actions = dict()
        self.parsers = dict()
        self.data = ""
        self.parsers = dict()
        self.actions = dict()
        self.matches = {}
        self.detectedType = set()

        logging.basicConfig(filename="log.log")
        self.log = logging.Logger("DataParser")
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)
        # create formatter
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        
        # add formatter to ch
        self.ch.setFormatter(self.formatter)
        self.log.addHandler(self.ch)
        self.parserModuleImport = self.moduleLoader(userTypeParser, 'userTypeParser')
        self.privateParserModuleImport = self.moduleLoader(userTypeParser.private, 'userTypeParser.private')
        self.ActionModuleImport = self.moduleLoader(userAction, 'userAction')
        self.privateActionModuleImport = self.moduleLoader(userAction.private, 'userAction.private')
        self.results = {}

    def moduleLoader(self, module_instance, module_name):
        """
        Load all class defined in `module_name` directory.
    
        Returns
        -------
         __import__('module_name',fromlist=parserModules)
    
        """
        parserModules = []
        files = os.listdir(module_instance.__path__[0])
        for file in files :
            if file.endswith(".py") and file != "__init__.py":
                parserModuleName = file.split(".")[0]
                parserModules.append(parserModuleName)
                self.log.info(f"Importing {parserModuleName} from {module_name}")
        # import all parser parserModule
        parserModuleImport = __import__(f'{module_name}',fromlist=parserModules)

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
        files+= os.listdir(userAction.private.__path__[0])
        for file in files :
            if file.endswith(".py") and file != "__init__.py":
                actionModule = file.split(".")[0]
                actionModules.append(actionModule)
                self.log.info("Importing {} action".format(actionModule))
        # import all parser parserModule
        actionModuleImport = __import__('userAction',fromlist=actionModules)
        actionModuleImport+= __import__('userAction.private',fromlist=actionModules)
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
        self.matches = {}
        self.detectedType = set()

        # Load all parsers
        parserModules = dict((name, m) for name, m
                           in getmembers(self.parserModuleImport, ismodule))
        privateParserModules = dict((name, m) for name, m
                           in getmembers(self.privateParserModuleImport, ismodule))
        parserModules.update(privateParserModules)

        for parserModule in parserModules.keys():
            classes = dict((name, c) for name, c 
                           in getmembers(parserModules[parserModule], isclass))
            for className in classes.keys():
                if "Parser" in className:
                    instance = classes[className](data)
                    if instance.contains():
                        self.matches.update({instance.parsertype: instance.extract()})
                        # Adding parser in a dict of all parsers relative to the input
                        self.parsers.update({instance.parsertype:instance})
                        self.log.debug("Paste contains {}".format(instance.parsertype))
                        self.detectedType.add(instance.parsertype)

        # Load all actions
        actionModules = dict((name, m) for name, m
                    in getmembers(self.ActionModuleImport, ismodule))
        privateActionModules = dict((name, m) for name, m
                    in getmembers(self.privateActionModuleImport, ismodule))
        actionModules.update(privateActionModules)

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

        self.results = {"matches" : self.matches, "detectedType" : self.detectedType, "actions": self.actions, "parsers":self.parsers}
        return self.results


if __name__=='__main__':
    a = clipParser()
    a.log.level = logging.debug
    data = "127.0.0.1, 124.0.12.23  user@domain.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    print(a.parseData(data))


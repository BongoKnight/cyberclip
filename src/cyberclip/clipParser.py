# -*- coding: utf-8 -*-

from inspect import getmembers, isfunction, isclass, ismodule, iscode
import userTypeParser
import userTypeParser.private

import userAction
import userAction.private

import re
import os
import logging
from pathlib import Path

        
class clipParser():
    
    def __init__(self, include="", exclude=""):
        self.actions = dict()
        self.parsers = dict()
        self.include = include
        self.exclude = exclude
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

    def moduleLoader(self, module_instance, module_name, include=".", exclude=""):
        """
        Load all class defined in `module_name` directory.
    
        Returns
        -------
         __import__('module_name',fromlist=parserModules)
    
        """
        parserModuleImport = []
        files = os.listdir(module_instance.__path__[0])
        for file in files :
            parserModules = []
            if self.verify_filename(file):
                parserModuleName = file.split(".")[0]
                parserModules.append(parserModuleName)
                self.log.info(f"Importing {parserModuleName} from {module_name}")
                # import all parser parserModule from file
                try:
                    parserModuleImport = __import__(f'{module_name}',fromlist=parserModules)
                except Exception as e:
                    self.log.error(f"Error while loading {parserModules} from {file} : {e}")
        return parserModuleImport

    def loadAction(self, include=".", exclude=""):
        """
        Load all actions defined in `action` directory.
    
        Returns
        -------
        __import__('userAction',fromlist=actionModules)    
        """

        files = os.listdir(userAction.__path__[0])
        files+= os.listdir(userAction.private.__path__[0])
        actionModuleImport = []
        for file in files :
            actionModules = []
            if self.verify_filename(file):
                actionModule = file.split(".")[0]
                actionModules.append(actionModule)
                self.log.info(f"Importing {actionModule} action")
                # import all parser parserModule from file
                try:
                    actionModuleImport+= __import__('userAction',fromlist=actionModules)
                    actionModuleImport+= __import__('userAction.private',fromlist=actionModules)
                except Exception as e:
                    self.log.error(f"Error while loading {actionModules} from {file} : {e}")
        return actionModuleImport
        
    def load_all(self):
        self.parsers = dict()
        self.actions = dict()
        data = ""

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
                    self.parsers.update({instance.parsertype:instance})

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
                        self.log.debug("Text might trigger an action : {}".format(instance.description))

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
                        self.log.debug("Text contains {}".format(instance.parsertype))
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
                        self.log.debug("Text might trigger an action : {}".format(instance.description))

        self.results = {"matches" : self.matches, "detectedType" : self.detectedType, "actions": self.actions, "parsers":self.parsers}
        return self.results
    
    def apply_actionable(self, actionable, text, complex_param = {}):
        self.parseData(text)
        if  "Action" in actionable.__module__ :
            if action := self.actions.get(actionable.description):
                if complex_param:
                    action.complex_param = complex_param
                result = action.execute()
                if isinstance(result, str):
                    return result
                elif isinstance(result, dict) and (mergedresult := result.get(text)):
                    return mergedresult
                else:
                    return result
        elif "Parser" in actionable.__module__:
            if parser := self.parsers.get(actionable.parsertype):
                return ", ".join(parser.extract())

    def verify_filename(self, file):
        is_valid = True
        if not (re.search(r"(Action|Parser)", file) or file.endswith(".py")):
            is_valid = False
        if"__init__" in file:
            is_valid = False
        if self.exclude:
            if re.search(self.exclude, file):
                is_valid = False
        if self.include:
            if not re.search(self.include, file):
                is_valid = False
            else:
                is_valid = True
        return is_valid

if __name__=='__main__':
    a = clipParser()
    a.log.level = logging.debug
    data = "127.0.0.1, 124.0.12.23  user@domain.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    print(a.parseData(data))


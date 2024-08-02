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
        self.results = {}
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

    def moduleLoader(self, module_instance, module_name, include=".", exclude=""):
        """
        Load all class defined in `module_name` directory.
    
        Returns
        -------
         __import__('module_name',fromlist=module_instance)
    
        """
        modules_imports = []
        files = os.listdir(module_instance.__path__[0])
        for file in files :
            modules = []
            if self.verify_filename(file):
                module_mainname = file.split(".")[0]
                modules.append(module_mainname)
                self.log.info(f"Importing {module_mainname} from {module_name}")
                # import all parser parserModule from file
                try:
                    modules_imports = __import__(f'{module_name}',fromlist=modules)
                except Exception as e:
                    self.log.error(f"Error while loading {modules} from {file} : {e}")
        return modules_imports
        
    async def create_instance(self, classes, class_name, arg):
        return classes[class_name](arg)

    async def load_all(self):
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
                    instance = await self.create_instance(classes, className, data)
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
                    instance = await self.create_instance(classes, className, self.parsers)
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
    
    async def apply_actionable(self, actionable, text, complex_param = {}) -> str:
        self.parseData(text)
        if  "Action" in actionable.__module__ :
            if action := self.actions.get(actionable.description):
                if complex_param:
                    action.complex_param = complex_param
                if actionable.complex_param:
                    action.complex_param = actionable.complex_param
                result = str(action)
                if isinstance(result, str):
                    return result
                elif isinstance(result, dict) and (mergedresult := result.get(text)):
                    return str(mergedresult)
                else:
                    return str(result)
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


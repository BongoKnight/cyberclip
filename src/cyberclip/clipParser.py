# -*- coding: utf-8 -*-

from inspect import getmembers, isfunction, isclass, ismodule, iscode
import traceback


import userTypeParser
import userTypeParser.private

import userAction
import userAction.private

import re
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

class clipParser():
    
    def __init__(self, include="", exclude=""):
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(funcName)s %(message)s",
            datefmt='[%X]',
            handlers=[],
            )

        self.actions = dict()
        self.parsers = dict()
        self.include = include
        self.exclude = exclude
        self.data = ""
        self.results = {}
        self.matches = {}
        self.detectedType = set()
        self.log = logging.getLogger(__name__)
        self.log.handlers = [RotatingFileHandler(filename=Path(__file__).parent / "log.log", maxBytes=5*1024*1024, backupCount=1)]
        # self.log.addHandler(RichHandler(rich_tracebacks=True, markup=True, level=logging.INFO))
        self.log.info("ClipParser created.")


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
                # self.log.info(f"Importing {module_mainname} from {module_name}")
                # import all parser parserModule from file
                try:
                    modules_imports = __import__(f'{module_name}',fromlist=modules)
                except Exception as e:
                    self.log.error(f"Error while loading {modules} from {file} : {e}")
        return modules_imports
        
    def create_instance(self, classes, class_name, arg):
        return classes[class_name](arg)

    def load_all(self):
        self.log.debug("Initiate parser and action loading." )
        self.parsers = dict()
        self.actions = dict()
        data = ""
        self.parserModuleImport = self.moduleLoader(userTypeParser, 'userTypeParser')
        self.privateParserModuleImport = self.moduleLoader(userTypeParser.private, 'userTypeParser.private')
        self.ActionModuleImport = self.moduleLoader(userAction, 'userAction')
        self.privateActionModuleImport = self.moduleLoader(userAction.private, 'userAction.private') 

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
                if "Parser" in className and "ParserInterface" not in className:
                    instance = self.create_instance(classes, className, data)
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
                if "Action" in className and not "ActionInterface" in className:
                    instance = self.create_instance(classes, className, self.parsers)
                    if hasattr(instance, "description"):
                        # Adding action in a dict of all parsers relative to the input
                        self.actions.update({instance.description : instance})

    def parseData(self, data):
        """
        Handle textual datas and return a dict containing matches and type of data detected.
    
        Returns
        -------
         {"matches" : matches, "detectedType" : detectedType, "actions": actions, "parsers": parsers}
    
        """
        self.log.debug("Parsing data")
        self.data = data
        self.matches = {}
        self.detectedType = set()

        if data:
            for parsertype, parser in self.parsers.items():
                parser.text = data
                if parser.contains():
                    self.detectedType.add(parsertype)
                    self.matches.update({parsertype: parser.extract()})
                else:
                    # Reset parser to avoid keeping old data in memory
                    parser.text = ""
                    parser.objects = {}

            for action in self.actions.values():
                action.parsers = {}
                for parsertype, parser in self.parsers.items():
                    if parsertype in action.supportedType and parsertype in self.detectedType:
                        # self.log.debug(f"Add parser: {parser.__class__}")
                        action.parsers.update({parsertype:parser})
            self.log.debug(f"Parsed data: {data[0:min(100,len(data))]}")        
        self.results = {"matches" : self.matches, "detectedType" : self.detectedType, "actions": self.actions, "parsers":self.parsers}
        return self.results
    
    
    async def apply_actionable(self, actionable, text, complex_param = {}) -> str:
        self.log.info(f"Applying {actionable.__class__}")
        self.parseData(text)
        if  "Action" in actionable.__module__ :
            if action := self.actions.get(actionable.description):
                if complex_param:
                    action.complex_param = complex_param
                if actionable.complex_param:
                    action.complex_param = actionable.complex_param
                self.log.debug(f"Action params : {actionable.complex_param}")
                self.log.debug(f"Action parsers : {",".join([str(parser.__class__) for parser in actionable.parsers.values()])}")
                result = str(action)
                self.log.debug(f"Action result : {result}")
                if isinstance(result, str):
                    return result
                elif isinstance(result, dict) and (mergedresult := result.get(text)):
                    return str(mergedresult)
                else:
                    return str(result)
        elif "Parser" in actionable.__module__:
            if parser := self.parsers.get(actionable.parsertype):
                return ", ".join(parser.extract())
        return "Action or parser not found"

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



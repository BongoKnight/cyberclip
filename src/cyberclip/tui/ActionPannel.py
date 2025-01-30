import re
import time
import asyncio
import traceback

from textual import on, work
from textual.reactive import var
from textual.containers import  VerticalScroll
from textual.widgets import Static, Button, Input, TabbedContent, TextArea
from textual.app import ComposeResult
from textual.command import Hit, Hits, Provider
from functools import partial

try:
    from userAction.actionInterface import actionInterface
    from userTypeParser.ParserInterface import ParserInterface
    from tui.RecipesPannel import Recipe
except:
    from cyberclip.userAction.actionInterface import actionInterface
    from cyberclip.userTypeParser.ParserInterface import ParserInterface
    from cyberclip.tui.RecipesPannel import Recipe



class ActionButton(Button):
    """A action widget for action specific to certain types of data."""
    DEFAULT_CSS="""
    """
    actionnable : actionInterface = var(None)
    action_supported_type = var({})
    
    def on_mount(self) -> None:
        self.label = self.action_name
        self.tooltip = self.actionnable.__doc__.splitlines()[0]
        if self.actionnable.indicators:
            self.styles.border_subtitle_color = "blue"
            self.border_subtitle = self.actionnable.indicators

    @property
    def action_name(self):
        return self.actionnable.description

    @on(Button.Pressed)
    def execute_option_action(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        from .ModalParamScreen import ParamScreen
        from .ContentView import ContentView
        if not self.action.complex_param :
            self.app.text = await self.app.parser.apply_actionable(self.action, self.app.query_one(TextArea).text)
        else:
            param_screen = ParamScreen()
            param_screen.border_title = f"Parameters for '{self.action.description}' action."
            param_screen.action = self.action
            try:
                self.app.push_screen(param_screen, partial(self.app.handle_param, self.action))
            except:
                self.app.notify(f"Error while executing action : {traceback.format_exc()}", severity="error")


class ActionCommands(Provider):
    """A command provider to return all actions for the current text."""

    def recover_actions(self) -> list[actionInterface | ParserInterface | Recipe]:
        """Get a list of all actions."""
        actions = list(self.app.parser.actions.values())
        parser = list(self.app.parser.parsers.values())
        recipes = self.app.recipes
        return actions + parser + recipes
    
    async def execute_action(self, actionable: ParserInterface | actionInterface | Recipe) -> None:
        """Event handler called when a  button is pressed."""
        from .ModalParamScreen import ParamScreen
        from .ContentView import ContentView
        from .TableView import FiltrableDataFrame
        
        try:
            if self.app.query_one(TabbedContent).active == "clipview":
                if self.app.query_one(ContentView):
                    self.app.parser.parseData(self.app.text)
                    if  "Action" in actionable.__module__ :
                        for desc, action in self.app.parser.actions.items():
                            if desc == actionable.description:
                                try:
                                    if not action.complex_param :
                                        self.app.text = await self.app.parser.apply_actionable(action, self.app.text)
                                    else:
                                        param_screen = ParamScreen()
                                        param_screen.border_title = f"Parameters for '{action.description}' action."
                                        param_screen.action = action
                                        self.app.push_screen(param_screen, partial(self.app.handle_param, action))
                                except Exception as e:
                                    self.app.notify("Error while applying action:" + str(e) + traceback.format_exc(), severity="error")

                    elif "Parser" in actionable.__module__:
                        for parsertype, parser in self.app.parser.parsers.items():
                            if parsertype == actionable.parsertype:
                                self.app.text = "\r\n".join(parser.extract())
                                break
                    elif isinstance(actionable, Recipe):
                        try:
                            self.app.text = await actionable.execute_recipe(self.app)
                        except Exception as e:
                            self.app.notify("Error while applying recipe: " + str(e) + traceback.format_exc(), severity="error")
            
            
            elif self.app.query_one(TabbedContent).active == "tableview":    
                dataframe = self.app.query_one(FiltrableDataFrame)
                if dataframe.visible:
                    column_name = dataframe.datatable.df.columns[dataframe.datatable.cursor_column]
                    
                    if  "Action" in actionable.__module__ :
                        for desc, action in self.app.parser.actions.items():
                            if desc == actionable.description:
                                new_column_name = dataframe.datatable.get_column_name(f"{actionable.__class__.__name__}_{column_name}")
                                if not actionable.complex_param :
                                    try:
                                        async with asyncio.timeout(10):
                                            dataframe.datatable.df[new_column_name] = await asyncio.gather(*(self.app.parser.apply_actionable(action, str(text)) for text in dataframe.datatable.df[column_name]))
                                            dataframe.datatable.update_displayed_df(dataframe.datatable.df)
                                    except Exception as e:
                                        self.app.notify("Error executing action: " + str(e), severity="error")
                                else:
                                    param_screen = ParamScreen()
                                    param_screen.border_title = f"Parameters for '{actionable.description}' action."
                                    param_screen.action = action
                                    try:
                                        self.app.push_screen(param_screen, partial(self.app.handle_param, action))
                                    except Exception as e:
                                        self.app.notify("Error applying action: " + str(e), severity="error")
                    elif "Parser" in actionable.__module__:
                        new_column_name = dataframe.datatable.get_column_name(f"{actionable.parsertype}_{column_name}")
                        try:
                            async with asyncio.timeout(10):
                                dataframe.datatable.df[new_column_name] = await asyncio.gather(*[self.app.parser.apply_actionable(actionable, str(text)) for text in dataframe.datatable.df[column_name]])
                                #dataframe.datatable.df[new_column_name] = dataframe.datatable.df[column_name].map(lambda text: asyncio.get_running_loop().create_task(self.app.parser.apply_actionable(actionable, str(text))).result(), na_action="ignore")
                                dataframe.datatable.update_displayed_df(dataframe.datatable.df, replace_df=True)
                        except Exception as e:
                            self.app.notify("Error while applying parser: " + str(e), severity="error")
                    elif isinstance(actionable, Recipe):
                        new_column_name = dataframe.datatable.get_column_name(f"{actionable.name}_{column_name}")
                        try:
                            self.app.notify("Applying recipe to a dataframe could take some times.")
                            async with asyncio.timeout(120):
                                dataframe.datatable.df[new_column_name] = await asyncio.gather(*[actionable.execute_recipe(self.app, text=text) for text in dataframe.datatable.df[column_name]])
                                dataframe.datatable.update_displayed_df(dataframe.datatable.df, replace_df=True)
                        except Exception as e:
                            self.app.notify("Error while applying recipe: " + str(e), severity="error")
        except Exception as e:
            self.app.notify("Error while applying: " + str(actionable.__class__) + traceback.format_exc(), severity="error")

    async def startup(self) -> None:  
        """Called once when the command palette is opened, prior to searching."""
        worker = self.app.run_worker(self.recover_actions, thread=True)
        self.actions = await worker.wait()

    async def search(self, query: str) -> Hits:  
        """Search for action."""
        matcher = self.matcher(query)
        for actionnable in self.actions:
            if  "Action" in actionnable.__module__ :
                action_desc = actionnable.description
                action_doc = actionnable.__doc__
                scoreDesc = matcher.match(action_desc) 
                scoreDoc = matcher.match(action_doc) 


                if scoreDesc > 0 or scoreDoc > 0:
                    if scoreDesc == max(scoreDesc, scoreDoc):
                        yield Hit(
                            scoreDesc,
                            matcher.highlight(action_desc),
                            partial(self.execute_action, actionnable),
                            help=action_doc.splitlines()[0],
                        )
                    else:
                        yield Hit(
                            scoreDoc,
                            matcher.highlight(action_desc),
                            partial(self.execute_action, actionnable),
                            help=action_doc.splitlines()[0],
                        )                        
            if  "Parser" in actionnable.__module__ :
                parser_desc = f"Extract {actionnable.parsertype}"
                parser_doc = actionnable.extract.__doc__
                scoreDesc = matcher.match(parser_desc) 
                scoreDoc = matcher.match(parser_doc) 
                if scoreDesc > 0 or scoreDoc > 0:
                    if scoreDesc == max(scoreDesc, scoreDoc):
                        yield Hit(
                            scoreDesc,
                            matcher.highlight(parser_desc),
                            partial(self.execute_action, actionnable),
                            help=parser_doc.splitlines()[0],
                        )
                    else:
                        yield Hit(
                            scoreDoc,
                            matcher.highlight(parser_desc),
                            partial(self.execute_action, actionnable),
                            help=parser_doc.splitlines()[0],
                        )
            if isinstance(actionnable, Recipe):
                recipe_desc = actionnable.name
                recipe_doc = actionnable.description
                scoreDesc = matcher.match(recipe_desc) 
                scoreDoc = matcher.match(recipe_doc) 
                if scoreDesc > 0 or scoreDoc > 0:
                    if scoreDesc == max(scoreDesc, scoreDoc):
                        yield Hit(
                            scoreDesc,
                            matcher.highlight(recipe_desc),
                            partial(self.execute_action, actionnable),
                            help=recipe_doc.splitlines()[0] if recipe_doc else "",
                        )
                    else:
                        yield Hit(
                            scoreDoc,
                            matcher.highlight(recipe_desc),
                            partial(self.execute_action, actionnable),
                            help=recipe_doc.splitlines()[0] if recipe_doc else "",
                        )        

class ActionPannel(Static):
    BINDINGS = [("escape", "clean_filter", "Clear the filter value."),]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter actions", id="action-filter")
        yield VerticalScroll(id="action-container")   

    def add_action(self, action_module: actionInterface) -> ActionButton:
        new_action = ActionButton()
        new_action.action = action_module
        new_action.action_name = action_module.description
        new_action.action_supported_type = set(action_module.supportedType)
        self.query_one("#action-container").mount(new_action)
        new_action.scroll_visible()
        return new_action

    def on_input_changed(self, event: Input.Changed) -> None:
        from .ContentView import ContentView
        self.app.query_one(ContentView).filter_action()


    def clean_filter(self):
        self.query_one(Input).value = ""
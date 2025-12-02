import asyncio
import traceback
from functools import partial
import re

from textual import on, work
from textual.reactive import var
from textual.containers import  VerticalScroll, Horizontal
from textual.widgets import Static, Button, Input, Switch, Label
from textual.app import ComposeResult
from textual.command import Hit, Hits, Provider

try:
    from userAction.actionInterface import actionInterface
    from userTypeParser.ParserInterface import ParserInterface
    from tui.RecipesPannel import Recipe
    from tui.DataTypePannel import DataTypeButton
except:
    from cyberclip.userAction.actionInterface import actionInterface
    from cyberclip.userTypeParser.ParserInterface import ParserInterface
    from cyberclip.tui.RecipesPannel import Recipe
    from cyberclip.tui.DataTypePannel import DataTypeButton



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
        self.app.get_param(self.actionnable)

class ActionCommands(Provider):
    """A command provider to return all actions for the current text."""
    
    def recover_actions(self) -> list[actionInterface | ParserInterface | Recipe]:
        """Get a list of all actions."""
        actions = list(self.app.parser.actions.values())
        parser = list(self.app.parser.parsers.values())
        recipes = self.app.recipes
        return actions + parser + recipes
    
    async def execute_recipe(self, actionable: Recipe) -> None:
        """Event handler called when a  button is pressed."""
        from .TableView import FiltrableDataFrame
        try:
            if self.app.active_tab == self.app.APP_TITLE:
                if self.app.contentview:
                    if isinstance(actionable, Recipe):
                        try:
                            self.app.text = await actionable.execute_recipe(self.app)
                        except Exception as e:
                            self.app.notify("Error while applying recipe: " + str(e) + traceback.format_exc(), severity="error")
            
            
            elif self.app.active_tab == "Table View":    
                dataframe = self.app.query_one(FiltrableDataFrame)
                if dataframe.visible:
                    column_name = dataframe.datatable.df.columns[dataframe.datatable.cursor_column]
                    if isinstance(actionable, Recipe):
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
                action_doc = actionnable.__doc__.splitlines()[0]
                scoreDesc = matcher.match(action_desc) 
                scoreDoc = matcher.match(action_doc) 
                if scoreDesc > 0.3 or scoreDoc > 0.3:
                    yield Hit(
                        scoreDesc,
                        matcher.highlight(action_desc),
                        partial(self.app.get_param, actionnable),
                        help=matcher.highlight(action_doc.splitlines()[0]),
                    )
                 
            elif  "Parser" in actionnable.__module__ :
                parser_desc = f"Extract {actionnable.parsertype}"
                parser_doc = actionnable.extract.__doc__.splitlines()[0]
                scoreDesc = matcher.match(parser_desc) 
                scoreDoc = matcher.match(parser_doc) 
                if scoreDesc > 0.3 or scoreDoc > 0.3:
                    yield Hit(
                        scoreDesc,
                        matcher.highlight(parser_desc),
                        partial(self.app.get_param, actionnable),
                        help=matcher.highlight(parser_doc.splitlines()[0]),
                    )

            elif isinstance(actionnable, Recipe):
                recipe_desc = actionnable.name
                recipe_doc = actionnable.description.splitlines()[0]
                scoreDesc = matcher.match(recipe_desc) 
                scoreDoc = matcher.match(recipe_doc) 
                if scoreDesc > 0.3 or scoreDoc > 0.3:
                    yield Hit(
                        scoreDesc,
                        matcher.highlight(recipe_desc),
                        partial(self.execute_recipe, actionnable),
                        help=matcher.highlight(recipe_doc.splitlines()[0]) if recipe_doc else "",
                    )    

class ActionPannel(Static):
    BINDINGS = [("escape", "clean_filter", "Clear the filter value."),]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter actions", id="action-filter")
        yield VerticalScroll(id="action-container")
        yield Horizontal(Switch(), Label("Display text actions"),id="textswitch")

    def add_action(self, action_module: actionInterface) -> ActionButton:
        new_action = ActionButton()
        new_action.actionnable = action_module
        new_action.action_supported_type = set(action_module.supportedType)
        self.query_one("#action-container").mount(new_action)
        new_action.scroll_visible()
        return new_action

    def filter_action(self):
        actionView = self.app.query_one(ActionPannel)
        if actionView:
            actions = actionView.query(ActionButton)
            actual_detected_type = set(self.app.parser.detectedType)
            for datatype_button in self.app.query(DataTypeButton):
                # Update actions supported_type and hide action buttons where no type are supported
                if datatype_button.switch and datatype_button.switch.value:
                    for action_button in actions:
                        # Add the supported type if the default action support it.
                        if datatype_button.parser_type in action_button.action_supported_type:
                            action_button.actionnable.supportedType.add(datatype_button.parser_type)
                else:
                    for action_button in actions:
                        if datatype_button.parser_type in action_button.action_supported_type:
                            action_button.actionnable.supportedType.discard(datatype_button.parser_type)
            
            filter_text = self.app.query_one(ActionPannel).query_one(Input).value
            for action_button in actions:
                if  (len(action_button.actionnable.supportedType.intersection(actual_detected_type)) >=1
                    and len(action_button.actionnable.supportedType.intersection(action_button.action_supported_type)) >= 1
                    ) :
                    action_button.visible = True
                    action_button.remove_class("no-height")
                    self.app.actions.append(action_button)
                    if filter_text:
                        for word in filter_text.split():
                            if not re.search(f"(?i){word}", action_button.actionnable.description, re.IGNORECASE):
                                if not word in action_button.actionnable.supportedType:
                                    action_button.visible = False
                                    action_button.add_class("no-height")
                else:
                    action_button.visible = False
                    action_button.add_class("no-height")
                if "text" in action_button.actionnable.supportedType and self.query_one(Switch).value == False:
                    action_button.visible = False
                    action_button.add_class("no-height")                    

    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_action()

    def on_switch_changed(self, event: Switch.Changed):
        self.filter_action()

    def clean_filter(self):
        self.query_one(Input).value = ""
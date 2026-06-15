import asyncio
import traceback
from functools import partial
import re

from textual import on, work
from textual.reactive import var
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Static, Button, Input, Switch, Label
from textual.app import ComposeResult
from textual.command import DiscoveryHit, Hit, Hits, Provider

try:
    from cyberclip.userAction.actionInterface import actionInterface
    from cyberclip.userTypeParser.ParserInterface import ParserInterface
    from cyberclip.tui.RecipesPannel import Recipe
    from cyberclip.tui.DataTypePannel import DataTypeButton
except ImportError:
    from userAction.actionInterface import actionInterface
    from userTypeParser.ParserInterface import ParserInterface
    from tui.RecipesPannel import Recipe
    from tui.DataTypePannel import DataTypeButton


class ActionButton(Button):
    """An action widget for action specific to certain types of data."""

    DEFAULT_CSS = """
    """
    actionnable: actionInterface = var(None)
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


async def execute_recipe(app, actionable: Recipe) -> None:
    from .TableView import FiltrableDataFrame

    try:
        if app.active_tab == app.APP_TITLE:
            if app.contentview and isinstance(actionable, Recipe):
                try:
                    app.text = await actionable.execute_recipe(app)
                except Exception as e:
                    app.notify(
                        "Error while applying recipe: "
                        + str(e)
                        + traceback.format_exc(),
                        severity="error",
                    )

        elif app.active_tab == "Table View":
            dataframe = app.query_one(FiltrableDataFrame)
            if dataframe.visible and isinstance(actionable, Recipe):
                column_name = dataframe.datatable.df.columns[
                    dataframe.datatable.cursor_column
                ]
                new_column_name = dataframe.datatable.get_column_name(
                    f"{actionable.name}_{column_name}"
                )
                try:
                    app.notify("Applying recipe to a dataframe could take some times.")
                    async with asyncio.timeout(120):
                        dataframe.datatable.df[new_column_name] = await asyncio.gather(
                            *[
                                actionable.execute_recipe(app, text=text)
                                for text in dataframe.datatable.df[column_name]
                            ]
                        )
                        dataframe.datatable.update_displayed_df(
                            dataframe.datatable.df, replace_df=True
                        )
                except Exception as e:
                    app.notify(
                        "Error while applying recipe: " + str(e), severity="error"
                    )
    except Exception:
        app.notify(
            "Error while applying: "
            + str(actionable.__class__)
            + traceback.format_exc(),
            severity="error",
        )


class RecipeActionButton(Button):
    DEFAULT_CSS = """
    """
    recipe: Recipe = var(None)

    def on_mount(self) -> None:
        self.label = self.recipe.name
        self.tooltip = self.recipe.description or "Saved recipe"
        self.styles.border_subtitle_color = "green"
        self.border_subtitle = "Recipe"

    @on(Button.Pressed)
    async def execute_recipe_button(self, event: Button.Pressed) -> None:
        await execute_recipe(self.app, self.recipe)


class ActionCommands(Provider):
    """A command provider to return system commands plus actions for the current text."""

    def recover_actions(self) -> list[actionInterface | ParserInterface | Recipe]:
        """Get a list of all actions."""
        actions = list(self.app.parser.actions.values())
        parser = list(self.app.parser.parsers.values())
        recipes = self.app.recipes
        return actions + parser + recipes

    def recover_system_commands(self):
        """Get the default app/system commands shown by Textual."""
        return list(self.app.get_system_commands(self.screen))

    @staticmethod
    def _matches_query(query: str, *values: str) -> bool:
        if not query:
            return True
        lowered_query = query.lower()
        return any(lowered_query in (value or "").lower() for value in values)

    async def execute_recipe(self, actionable: Recipe) -> None:
        """Event handler called when a  button is pressed."""
        await execute_recipe(self.app, actionable)

    async def startup(self) -> None:
        """Called once when the command palette is opened, prior to searching."""
        self.actions = self.recover_actions()

    async def discover(self) -> Hits:
        """Show default system commands first, then enabled actions and recipes."""
        for name, help_text, callback, discover in self.recover_system_commands():
            if discover:
                yield DiscoveryHit(name, callback, help=help_text)

        self.actions = self.recover_actions()
        for actionnable in self.actions:
            if "Action" in actionnable.__module__:
                action_desc = actionnable.description
                action_doc = (actionnable.__doc__ or "").splitlines()
                action_doc = action_doc[0] if action_doc else ""
                yield DiscoveryHit(
                    action_desc,
                    partial(self.app.get_param, actionnable),
                    text=action_desc,
                    help=action_doc or None,
                )
            elif "Parser" in actionnable.__module__:
                parser_desc = f"Extract {actionnable.parsertype}"
                parser_doc = (actionnable.extract.__doc__ or "").splitlines()
                parser_doc = parser_doc[0] if parser_doc else ""
                yield DiscoveryHit(
                    parser_desc,
                    partial(self.app.get_param, actionnable),
                    text=parser_desc,
                    help=parser_doc or None,
                )
            elif isinstance(actionnable, Recipe):
                recipe_desc = actionnable.name
                recipe_doc = actionnable.description.splitlines()
                recipe_doc = recipe_doc[0] if recipe_doc else ""
                yield DiscoveryHit(
                    recipe_desc,
                    partial(self.execute_recipe, actionnable),
                    text=recipe_desc,
                    help=recipe_doc or "Recipe",
                )

    async def search(self, query: str) -> Hits:
        """Search for action."""
        query = query.strip()
        matcher = self.matcher(query)

        for name, help_text, callback, *_ in self.recover_system_commands():
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    callback,
                    text=name,
                    help=help_text,
                )

        self.actions = self.recover_actions()
        for actionnable in self.actions:
            if "Action" in actionnable.__module__:
                action_desc = actionnable.description
                action_doc = (actionnable.__doc__ or "").splitlines()
                action_doc = action_doc[0] if action_doc else ""
                scoreDesc = matcher.match(action_desc)
                scoreDoc = matcher.match(action_doc)
                score = max(scoreDesc, scoreDoc)
                if self._matches_query(query, action_desc, action_doc) or score > 0:
                    yield Hit(
                        score or 1.0,
                        matcher.highlight(action_desc),
                        partial(self.app.get_param, actionnable),
                        text=action_desc,
                        help=matcher.highlight(action_doc) if action_doc else "",
                    )

            elif "Parser" in actionnable.__module__:
                parser_desc = f"Extract {actionnable.parsertype}"
                parser_doc = (actionnable.extract.__doc__ or "").splitlines()
                parser_doc = parser_doc[0] if parser_doc else ""
                scoreDesc = matcher.match(parser_desc)
                scoreDoc = matcher.match(parser_doc)
                score = max(scoreDesc, scoreDoc)
                if self._matches_query(query, parser_desc, parser_doc) or score > 0:
                    yield Hit(
                        score or 1.0,
                        matcher.highlight(parser_desc),
                        partial(self.app.get_param, actionnable),
                        text=parser_desc,
                        help=matcher.highlight(parser_doc) if parser_doc else "",
                    )

            elif isinstance(actionnable, Recipe):
                recipe_desc = actionnable.name
                recipe_doc = actionnable.description.splitlines()
                recipe_doc = recipe_doc[0] if recipe_doc else ""
                scoreDesc = matcher.match(recipe_desc)
                scoreDoc = matcher.match(recipe_doc)
                score = max(scoreDesc, scoreDoc)
                if self._matches_query(query, recipe_desc, recipe_doc) or score > 0:
                    yield Hit(
                        score or 1.0,
                        matcher.highlight(recipe_desc),
                        partial(self.execute_recipe, actionnable),
                        text=recipe_desc,
                        help=matcher.highlight(recipe_doc) if recipe_doc else "",
                    )


class ActionPannel(Static):
    BINDINGS = [
        ("escape", "clean_filter", "Clear the filter value."),
    ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter actions", id="action-filter")
        yield VerticalScroll(id="action-container")
        yield Horizontal(Switch(), Label("Display text actions"), id="textswitch")

    def add_action(self, action_module: actionInterface) -> ActionButton:
        new_action = ActionButton()
        new_action.actionnable = action_module
        new_action.action_supported_type = set(action_module.supportedType)
        self.query_one("#action-container").mount(new_action)
        new_action.scroll_visible()
        return new_action

    def add_recipe(self, recipe: Recipe) -> RecipeActionButton:
        new_recipe = RecipeActionButton()
        new_recipe.recipe = recipe
        self.query_one("#action-container").mount(new_recipe)
        return new_recipe

    def refresh_recipe_buttons(self):
        for recipe_button in list(self.query(RecipeActionButton)):
            recipe_button.remove()
        for recipe in sorted(self.app.recipes, key=lambda recipe: recipe.name.lower()):
            self.add_recipe(recipe)

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
                        if (
                            datatype_button.parser_type
                            in action_button.action_supported_type
                        ):
                            action_button.actionnable.supportedType.add(
                                datatype_button.parser_type
                            )
                else:
                    for action_button in actions:
                        if (
                            datatype_button.parser_type
                            in action_button.action_supported_type
                        ):
                            action_button.actionnable.supportedType.discard(
                                datatype_button.parser_type
                            )

            filter_text = self.app.query_one(ActionPannel).query_one(Input).value
            for action_button in actions:
                if (
                    len(
                        action_button.actionnable.supportedType.intersection(
                            actual_detected_type
                        )
                    )
                    >= 1
                    and len(
                        action_button.actionnable.supportedType.intersection(
                            action_button.action_supported_type
                        )
                    )
                    >= 1
                ):
                    action_button.visible = True
                    action_button.remove_class("no-height")
                    self.app.actions.append(action_button)
                    if filter_text:
                        for word in filter_text.split():
                            if not re.search(
                                f"(?i){word}",
                                action_button.actionnable.description,
                                re.IGNORECASE,
                            ):
                                if not word in action_button.actionnable.supportedType:
                                    action_button.visible = False
                                    action_button.add_class("no-height")
                else:
                    action_button.visible = False
                    action_button.add_class("no-height")
                if (
                    "text" in action_button.actionnable.supportedType
                    and self.query_one(Switch).value == False
                ):
                    action_button.visible = False
                    action_button.add_class("no-height")

            for recipe_button in actionView.query(RecipeActionButton):
                recipe_button.visible = False
                recipe_button.add_class("no-height")
                if filter_text:
                    recipe_text = (
                        f"{recipe_button.recipe.name}\n"
                        f"{recipe_button.recipe.description}"
                    )
                    matches_recipe = True
                    for word in filter_text.split():
                        if not re.search(f"(?i){word}", recipe_text, re.IGNORECASE):
                            matches_recipe = False
                            break
                    if matches_recipe:
                        recipe_button.visible = True
                        recipe_button.remove_class("no-height")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_action()

    def on_switch_changed(self, event: Switch.Changed):
        self.filter_action()

    def clean_filter(self):
        self.query_one(Input).value = ""

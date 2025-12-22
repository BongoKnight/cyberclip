import yaml
from functools import partial
from dataclasses import dataclass
from pathlib import Path

from textual import on, work
from textual.app import App
from textual.screen import ModalScreen
from textual.message import Message
from textual.reactive import var, reactive
from textual.containers import  Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Button, Input, Label, TextArea, Switch, Select
from textual.app import ComposeResult


try:
    from userAction.actionInterface import actionInterface
    from userTypeParser.ParserInterface import ParserInterface
except:
    from cyberclip.userAction.actionInterface import actionInterface
    from cyberclip.userTypeParser.ParserInterface import ParserInterface

# eq and frozen allow for this class to be hashable, which is needed to be included as return option of a Select widget
@dataclass(eq=True, frozen=True)
class ActionnableDescriptor:
    actionnable : ParserInterface | actionInterface
    description : str
    type: str

@dataclass
class RecipeStep:
    step_dict: dict 
    actionnable : ActionnableDescriptor = None

    @property
    def actionnableName(self):
        return self.step_dict.get("actionnableName", "")
    
    @actionnableName.setter
    def actionnableName(self, value):
        assert type(value) == str
        self.step_dict["actionnableName"] = value

    @property
    def usePreset(self):
        return self.step_dict.get("usePreset", True)
    
    @property
    def params(self):
        return self.step_dict.get("complex_param", {})
    
    @params.setter
    def params(self, value):
        assert type(value) == dict
        self.step_dict["complex_param"] = value

    def find_actionnable(self, app, actionnable_description: str) -> ActionnableDescriptor:
        for action in app.recipe_parser.actions.values():
            if action.description == actionnable_description:
                self.actionnable = ActionnableDescriptor(action, action.description, type="action")
                return ActionnableDescriptor(action, action.description, type="action")
        for parser in app.recipe_parser.parsers.values():
            if f"Extract {parser.parsertype}" == actionnable_description:
                self.actionnable = ActionnableDescriptor(parser, f"Extract {parser.parsertype}", "parser")
                return self.actionnable
    def to_dict(self):
        return {"actionnableName":self.actionnableName, "usePreset":self.usePreset, "complex_param":self.params}

@dataclass
class Recipe:
    recipe_dict: dict 

    @property
    def steps(self):
        return [RecipeStep(step_dict=i) for i in self.recipe_dict.get("steps",[])]
    
    @property
    def description(self):
        return self.recipe_dict.get("description","")

    @property
    def name(self):
        return self.recipe_dict.get("name","")
    
    def to_dict(self):
        return {"name":self.name,
                "description":self.description,
                "steps":[step.to_dict() for step in self.steps]
                }
    
    @name.setter
    def name(self, value):
        assert type(value) == str
        self.recipe_dict["name"] = value

    @description.setter
    def description(self, value):
        assert type(value) == str
        self.recipe_dict["description"] = value

    @steps.setter
    def steps(self, value):
        assert type(value) == list
        self.recipe_dict["steps"] = value
    

    async def execute_recipe(self, app: App, text=None, step_index=0):
        # TODO always use handleParam
        from .ModalParamScreen import ParamScreen
        new_text = ""
        nb_step = len(self.steps)
        if text == None:
             new_text = app.text
        else:
            new_text = text
        app.recipe_parser.parseData(new_text)
        if step_index < nb_step:
            step = self.steps[step_index]
            if step.find_actionnable(app, step.actionnableName):
                if step.actionnable.type == "action":
                    if step.usePreset:
                        if step.params:
                            step.actionnable.actionnable.complex_param = step.params
                        new_text = await app.recipe_parser.apply_actionable(step.actionnable.actionnable, new_text)
                        return await self.execute_recipe(app, text=new_text, step_index=step_index+1)         
                    else:
                        async with app.get_param(step.actionnable.actionnable):
                           return await self.execute_recipe(app, text=app.text, step_index=step_index+1)
                elif step.actionnable.type == "parser":
                    new_text = "\r\n".join(step.actionnable.actionnable.extract())
                    return await self.execute_recipe(app, text=new_text, step_index=step_index+1)
            else:
                app.notify(f"Error retrievig action : {step.actionnableName}", severity="warning")
        else:
            return new_text


class RecipesPannel(Static):

    DEFAULT_CSS = """
    #recipes-container{
        width: 1fr;
    }
    #recipe-viewer{
        width: 2fr;
        padding: 1;
        border: $accent round;
    }
    #recipes_actions{
        height: 5;
    }
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(Button("Save recipes", variant="success", id="save_recipes"), Button("Create recipe", variant="primary", id="create_recipe"), id="recipes_actions")
        yield Horizontal(VerticalScroll(id="recipes-container"), VerticalScroll(id="recipe-viewer"))

    def refresh_recipes(self):
        recipes_container = self.query_one("#recipes-container", VerticalScroll)
        recipes_container.remove_children()
        self.app.recipes.sort(key=lambda recipe: recipe.name)
        for recipe in self.app.recipes:
            new_button = RecipeButton()
            recipes_container.mount(new_button)
            new_button.recipe = recipe

    @on(Button.Pressed, "#create_recipe")
    def create_recipe(self):
        recipes_container = self.query_one("#recipes-container", VerticalScroll)
        new_button = RecipeButton()
        recipes_container.mount(new_button)
        new_button.recipe = Recipe({"name":"New recipe","description":"", "steps":[]})



    @on(Button.Pressed, "#save_recipes")
    def save_recipes(self):
        recipes = []
        all_valid = True
        for recipe_widget in self.query(RecipeButton):
            is_valid = True
            if not recipe_widget.recipe.name:
                is_valid = False
                all_valid = False
                self.notify("⚠️ One of your recipe has no name.", severity="warning")
            if not recipe_widget.recipe.description:
                is_valid = False
                all_valid = False
                self.notify(f"⚠️ Recipe {recipe_widget.recipe.name} has no description.", severity="warning")
            for step in recipe_widget.recipe.steps:
                if isinstance(step.params, str):
                    self.notify(f"⚠️ Recipe {recipe_widget.recipe.name} contains an invalid step : {step.actionnableName}", severity="warning")
                    is_valid = False
                    all_valid = False
            if is_valid:
                recipes.append(recipe_widget.recipe.to_dict())
        if all_valid:
            self.app.recipes = [Recipe(recipe_dict=recipe) for recipe in recipes]
            with open(Path(__file__).parent / '../data/recipes.yml', "w+", encoding="utf8") as f:
                rules = yaml.dump(recipes)
                f.write(rules)
                self.notify("☑  Recipes saved!")
            self.refresh_recipes()


class RecipeButton(Button):
    DEFAULT_CSS = """
    RecipeButton{
        width: 1fr;
    }
    """
    recipe = reactive(Recipe(recipe_dict={}))
    def watch_recipe(self, recipe: Recipe):
        self.label = recipe.name
        self.refresh()

    @on(Button.Pressed)
    def show_info(self):
        viewer = self.app.query_one("#recipe-viewer", VerticalScroll)
        viewer.remove_children()
        recipe_widget = RecipeWidget()
        recipe_widget.button = self
        viewer.mount(recipe_widget)



class StepWidget(Static):
    DEFAULT_CSS = """    
    .step{
        border: $primary;
        height: 20;
    }
    .title {
        margin-top: 1;
    }
    .name{
        height: 3;
    }    
    """
    step = var(RecipeStep(step_dict={}))

    class Changed(Message):
        def __init__(self) -> None:
            super().__init__()

    def compose(self) -> ComposeResult:
            params = ""
            try:
                params = yaml.dump(self.step.params)
            except:
                params = self.step.params
            step_widget = VerticalScroll(Horizontal(Label("Use preset ? :", classes="title"), Switch(self.step.usePreset), Button("Change action", variant="primary", id="change"), Button("Delete step", variant="error", id="delete"), classes="name") ,TextArea(params, show_line_numbers=True, language="yaml") ,classes="step")
            step_widget.border_title = self.step.actionnableName
            yield step_widget

    def on_mount(self):
        self.step.actionnable = self.step.find_actionnable(self.app, self.step.actionnableName)

    @on(TextArea.Changed)
    @on(Switch.Changed)
    @on(Button.Pressed)
    def emit_change(self):
        self.update_step()
        self.post_message(self.Changed())

                

    def update_step(self):
        usePreset = self.query_one(Switch).value
        try:
            params = yaml.safe_load(self.query_one(TextArea).text)
        except Exception as e:
            params =  self.query_one(TextArea).text
        self.step.step_dict.update({"usePreset":usePreset, "complex_param":params})

    @on(Button.Pressed, "#delete")
    def delete_step(self):
        self.remove()

    @on(Button.Pressed, "#change")
    def change_step(self):
        def update_actionnable(actionnable: ActionnableDescriptor):
            if actionnable:
                self.step.actionnableName = str(actionnable.description)
                self.query_one(".step", VerticalScroll).border_title = self.step.actionnableName
                self.actionnable = actionnable
                if actionnable.type == "action":
                    self.step.params = actionnable.actionnable.complex_param
                    self.query_one(TextArea).clear()
                    self.query_one(TextArea).insert(yaml.dump(self.step.params))
                    self.query_one(TextArea).disabled = False
                    self.query_one(Switch).value = True
                elif actionnable.type == "parser":
                    self.step.params = {}
                    self.query_one(TextArea).clear()
                    self.query_one(TextArea).disabled = True
                    self.query_one(Switch).value = False
                    self.query_one(Switch).disabled = True

        select_screen = SelectActionnableScreen()
        self.app.push_screen(select_screen, update_actionnable)




class SelectActionnableScreen(ModalScreen):
    """Modal screen for selecting actionnable"""
    DEFAULT_CSS = """
    SelectActionnableScreen {
        align: center middle;
        background: black 30%;
        layout: vertical;

    }
    #dialog {
        padding: 3 3;
        width: 80%;
        height: 20;
        border: $primary;
        }
    
    #submit {
        height: 3;
        align-horizontal: right;
        dock: bottom;
    }
    """

    BINDINGS = [("escape", "app.pop_screen", "Escape selection screen.")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Select([], allow_blank=True),
            Horizontal(
                Button("Save params", variant="primary", id="save"),
                Button("Cancel", variant="error", id="cancel"), id="submit"
            ),
            id="dialog"
        )



    async def on_mount(self) -> None:
        self.query_one("#dialog").border_title = "Select an action"
        actions = list(self.app.recipe_parser.actions.values())
        parsers = list(self.app.recipe_parser.parsers.values())
        actionnables = actions + parsers
        actionnable_tupples = []
        for actionnable in actionnables:
            if  "Action" in actionnable.__module__ :
                actionnable_desc = ActionnableDescriptor(actionnable=actionnable, description=actionnable.description, type="action")
            if  "Parser" in actionnable.__module__ :
                actionnable_desc = ActionnableDescriptor(actionnable=actionnable, description=f"Extract {actionnable.parsertype}", type="parser")
            if actionnable_desc:
                actionnable_tupples.append((actionnable_desc.description, actionnable_desc))
        if actionnable_tupples:
            actionnable_tupples.sort(key=lambda x : x[0])
        select = self.query_one(Select)
        select.set_options(actionnable_tupples)
        select._allow_blank = False


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss({})
        else:
            select = self.query_one(Select)
            self.dismiss(result=select.value if not select.is_blank() else None)

class RecipeWidget(Static):
    DEFAULT_CSS = """
    .title {
        margin-top: 1;
        width: 15;
    }
    .name{
        height: 3;
    }
    #option{
        height: 3;
    }
    """
    button = var(RecipeButton())
    def compose(self) -> ComposeResult:
        yield Horizontal(Label("Name :", classes="title"), Input(self.button.recipe.name, placeholder="Enter recipe title...", id="recipename"), classes="name")
        yield Horizontal(Label("Description :", classes="title"), Input(self.button.recipe.description, placeholder="Enter description...", id="recipedesc"), classes="name")
        steps_widgets = []
        for step in self.button.recipe.steps:
            step_widget = StepWidget()
            step_widget.step = step
            steps_widgets.append(step_widget)
        yield VerticalScroll(*steps_widgets, id="stepslist")
        yield Horizontal(Button("Add step", variant="primary", id="add_step"), Button("Delete recipe", variant="error", id="delete_recipe"), id="option")


    @on(Button.Pressed, "#add_step")
    def add_step(self):
        self.button.recipe.steps = [i.to_dict() for i in self.button.recipe.steps] + [{}]
        stepslist = self.query_one("#stepslist", VerticalScroll)
        stepslist.remove_children()
        for step in self.button.recipe.steps:
            step_widget = StepWidget()
            step_widget.step = step
            stepslist.mount(step_widget)

    @on(Button.Pressed, "#delete_recipe")
    async def delete_recipe(self, event: Button.Pressed):
        await self.button.remove()
        self.app.query_one(RecipesPannel).save_recipes()
        self.app.query_one(RecipesPannel).refresh_recipes()

    @on(Input.Changed)
    @on(Button.Pressed)
    @on(StepWidget.Changed)
    def update_recipe(self):
        self.button.recipe.name = self.query_one("#recipename", Input).value
        self.button.recipe.description = self.query_one("#recipedesc", Input).value
        steps = []
        steps_widgets = self.query(StepWidget)
        for step_widget in steps_widgets:
            steps.append(step_widget.step.step_dict)
        self.button.recipe.steps = steps

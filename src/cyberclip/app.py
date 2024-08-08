import sys
import pyperclip
from io import StringIO
import pandas as pd
import traceback
from pathlib import Path
import yaml
import asyncio

from textual import on, work
from textual.reactive import var, reactive
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.containers import Grid
from textual.driver import Driver
from textual.widgets import Footer, TabbedContent, TabPane, TextArea

try:
    from cyberclip.tui.ConfigScreen import ConfigScreen
    from cyberclip.tui.DataTypePannel import DataLoader
    from cyberclip.tui.ContentView import ContentView
    from cyberclip.tui.ActionPannel import ActionPannel, ActionCommands
    from cyberclip.tui.TableView import FiltrableDataFrame
    from cyberclip.tui.RecipesPannel import RecipesPannel, RecipeButton, Recipe
    from cyberclip.userTypeParser import TSVParser
    from cyberclip.clipParser import clipParser
    from cyberclip.userAction import actionInterface
    from cyberclip.clipboardHandler import get_clipboard_text
except:
    from tui.ConfigScreen import ConfigScreen
    from tui.DataTypePannel import DataLoader
    from tui.ContentView import ContentView
    from tui.ActionPannel import ActionPannel, ActionCommands
    from tui.TableView import FiltrableDataFrame
    from tui.RecipesPannel import RecipesPannel, RecipeButton, Recipe
    from userTypeParser import TSVParser
    from clipParser import clipParser
    from userAction import actionInterface
    from clipboardHandler import get_clipboard_text




class ClipBrowser(App):
    """This class implements the `App` class from `textual`. It defines the layout of the Terminal 
    User Interface (TUI).  

    Attributes:
        text (str): Store the text available in all the application, this text is usually 
            updated with data contained in the clipboard.
        parser (clipParser): A text parser that parse text to extract valuable data (thanks to `userTypeParser`) 
            and execute action based on the data extracted (thanks to `userAction`).
        
    
    """
    CSS_PATH = "app.scss"
    COMMANDS = {ActionCommands}
    SCREENS = {"conf": ConfigScreen}
    BINDINGS = [
        ("ctrl+p", "command_palette","Command palette"),
        ("ctrl+s", "save", "Save actual view."),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+f", "select_action_filter", "Filter"),
        ("ctrl+b", "copy", "Copy actual content to clipboard."),
        ("ctrl+r", "reset", "Reset content view to clipboard content."),
        ("ctrl+e", "push_screen('conf')", "Edit config")
    ]
    CLOSE_TIMEOUT = None

    parser = var(clipParser())
    recipe_parser = var(clipParser())
    text = reactive("Waiting for Update...")
    try:
        with open(Path(__file__).parent / 'data/recipes.yml', "r", encoding="utf8") as f:
            recipes = var([Recipe(recipe_dict=i) for i in yaml.safe_load(f.read())])
    except Exception as e:
        recipes = var([])
        print("Error loading recipes...", e)

    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)
        self.actions = []

    async def on_mount(self):
        await self.parser.load_all()
        await self.recipe_parser.load_all()
        # self.app.notify(f"Parsers chargés: {len(self.parser.parsers.keys())}\nActions chargées: {len(self.parser.actions.keys())}")

    def compose(self) -> ComposeResult:
        """Compose the main UI. Generate three tabs corresponding to the three modes of the application :
        
        - Main view which displays the content of keyboard, parser extractors on left and actions on right.
        - Table view for sorting and filtering results of action or to enrich tabular data/files.
        - Rules view for managing rules to apply to data (chains of actions with defined parameters), 
        the rules became new actions available in the command pallette. 

        Warning: 
            Table and rule views are a WIP.

        """
        self.console.set_window_title("📝CyberClip👩‍💻")
        with TabbedContent(id="maintabs"):
            with TabPane("📝CyberClip👩‍💻", id="clipview"):
                yield Grid(
                    DataLoader(id="left-pannel"),
                    ContentView(id="content-view"),
                    ActionPannel(id="action-pannel"),
                    id="maingrid"
                )
            with TabPane('TableView', id="tableview"):
                yield FiltrableDataFrame(pd.DataFrame(), id="main-table")
            with TabPane('Recipes', id="recipes"):
                yield RecipesPannel()
        yield Footer()

    def action_quit(self):
        sys.exit()

    def action_save(self):      
        with open("clipboard.txt", "w") as f:
            f.write(self.text)

    def action_copy(self):
        pyperclip.copy(self.text)
        self.notify("Copied in clipboard!")

    def action_reset(self):
        self.text = get_clipboard_text()

    def action_select_action_filter(self):
        filter = self.app.query_one("#action-filter").focus()
        filter.value = ""

    @property
    def contentview(self):
        return self.query_one(ContentView)

    @on(TabbedContent.TabActivated)
    def check_TSV(self, event: TabbedContent.TabActivated):
        if event.tab.label_text == "TableView":
            df = pd.DataFrame()
            parser = TSVParser.tsvParser(self.text)
            if parser.extract():            
                try:
                    df = pd.read_csv(StringIO(self.text), sep="\t", header=None, skip_blank_lines=False)
                    df.columns = [str(i) for i in df.columns]
                    self.app.call_after_refresh(self.update_dataframe, df)
                except Exception as e:
                    self.app.notify(f"Error : {str(e)}" ,title="Error while loading data...", timeout=5, severity="error")
        if event.tab.label_text == "📝CyberClip👩‍💻":
            self.parser.parseData(self.text)
        if event.tab.label_text == "Recipes":
            self.query_one(RecipesPannel).refresh_recipes()
            if querybuttons:= self.query(RecipeButton):
                querybuttons[0].press()

    def update_dataframe(self, df):
        tab = self.query_one("#tableview")
        tab.remove_children()
        tab.mount(FiltrableDataFrame(pd.DataFrame(df), id="main-table"))

    def watch_text(self, new_text: str) -> None:
        if self.text:
            self.parser.parseData(self.text)
            self.query_one(ContentView).update_text(new_text)
            self.query_one(ContentView).filter_action()


    @work(exclusive=True)
    async def handle_param(self, action : actionInterface ,  complex_param : dict | None = None, recipe_parser : bool = False):
        if complex_param :
            action.complex_param = complex_param
        if self.query_one("#maintabs", TabbedContent).active == "clipview":
            try:
                self.text = await self.parser.apply_actionable(action, self.text)
            except Exception as e:
                self.app.notify("Error applying action..." + str(e) + traceback.format_exc(), severity="error")  
        elif self.query_one("#maintabs", TabbedContent).active == "tableview":
            dataframe = self.query_one(FiltrableDataFrame)
            column_name = dataframe.datatable.df.columns[dataframe.datatable.cursor_column]
            new_column_name = dataframe.datatable.get_column_name(f"{action.__class__.__name__}_{column_name}")
            try:
                async with asyncio.timeout(10):
                    if recipe_parser:
                        dataframe.datatable.df[new_column_name] = await asyncio.gather(*(self.recipe_parser.apply_actionable(action, str(text)) for text in dataframe.datatable.df[column_name]))
                        dataframe.datatable.update_displayed_df(dataframe.datatable.df)
                    else:
                        dataframe.datatable.df[new_column_name] = await asyncio.gather(*(self.parser.apply_actionable(action, str(text)) for text in dataframe.datatable.df[column_name]))
                        dataframe.datatable.update_displayed_df(dataframe.datatable.df)    
            except Exception as e:
                self.app.notify("Action took too long to execute..." + str(e) + traceback.format_exc(), severity="error")

    


def main():
    cyberClip = ClipBrowser()
    cyberClip.run()

if __name__ == "__main__":
    main()
import sys
from typing import Type
import pyperclip
from io import StringIO
import pandas as pd


from textual import on
from textual.reactive import var, reactive
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.containers import Grid
from textual.driver import Driver
from textual.widgets import Footer, TabbedContent, TabPane, Label

try:
    from cyberclip.tui.ConfigScreen import ConfigScreen
    from cyberclip.tui.DataTypePannel import DataLoader
    from cyberclip.tui.ContentView import ContentView
    from cyberclip.tui.ActionPannel import ActionPannel, ActionCommands
    from cyberclip.tui.TableView import FiltrableDataFrame
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

    parser = var(clipParser())
    text= reactive("Waiting for Update...")

    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)
        self.actions = []

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
        with TabbedContent():
            with TabPane("📝CyberClip👩‍💻"):
                yield Grid(
                    DataLoader(id="left-pannel"),
                    ContentView(id="content-view"),
                    ActionPannel(id="action-pannel"),
                    id="maingrid"
                )
            with TabPane('TableView', id="table-view"):
                yield FiltrableDataFrame(pd.DataFrame(), id="main-table")
            with TabPane('Recipes'):
                yield Label("Recipes")
        yield Footer()

    def action_quit(self):
        sys.exit()

    def action_save(self):      
        with open("clipboard.txt", "w") as f:
            f.write(self.text)

    def action_copy(self):
        pyperclip.copy(self.text)

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
                    df = pd.read_csv(StringIO(self.text), sep="\t",header=None)
                    df.columns = [str(i) for i in df.columns]
                    self.app.call_after_refresh(self.update_dataframe, df)
                except Exception as e:
                    self.app.notify(f"Error : {str(e)}",title="Error while loading data...",timeout=5, severity="error")
    
    def update_dataframe(self, df):
        tab = self.query_one("#table-view")
        tab.remove_children()
        tab.mount(FiltrableDataFrame(pd.DataFrame(df), id="main-table"))

    def watch_text(self, new_text: str) -> None:
        self.query_one(ContentView).update_text(new_text)

    def handle_param(self, action : actionInterface , complex_param : dict):
        if complex_param :
            action.complex_param = complex_param
            self.text = str(action)
    

def main():
    ClipBrowser().run()

if __name__ == "__main__":
    main()
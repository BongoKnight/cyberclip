import sys
import argparse
from io import StringIO
import pandas as pd
import traceback
from pathlib import Path
import yaml
import asyncio
from functools import partial

from textual import on, work
from textual.theme import Theme
from textual.binding import Binding
from textual.reactive import var, reactive
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.containers import Grid
from textual.driver import Driver
from textual.widgets import Footer, TabbedContent, TabPane, TextArea
from netext.textual_widget.widget import GraphView

try:
    from cyberclip.tui.DataTypePannel import DataLoader
    from cyberclip.tui.GraphPannel import GraphPannel
    from cyberclip.tui.ContentView import ContentView
    from cyberclip.tui.ActionPannel import ActionPannel, ActionCommands
    from cyberclip.tui.TableView import FiltrableDataFrame
    from cyberclip.tui.RecipesPannel import RecipesPannel, RecipeButton, Recipe
    from cyberclip.tui.ModalParamScreen import ParamScreen
    from cyberclip.userTypeParser import TSVParser
    from cyberclip.clipParser import clipParser
    from cyberclip.userAction.actionInterface import actionInterface
    from cyberclip.userTypeParser.ParserInterface import ParserInterface
    from cyberclip.clipboardHandler import get_clipboard_text
    from cyberclip.utilities import clean_tsv
except:
    from tui.DataTypePannel import DataLoader
    from tui.ContentView import ContentView
    from tui.GraphPannel import GraphPannel
    from tui.ActionPannel import ActionPannel, ActionCommands
    from tui.TableView import FiltrableDataFrame
    from tui.RecipesPannel import RecipesPannel, RecipeButton, Recipe
    from tui.ModalParamScreen import ParamScreen
    from userTypeParser import TSVParser
    from clipParser import clipParser
    from userAction.actionInterface import actionInterface
    from userTypeParser.ParserInterface import ParserInterface
    from clipboardHandler import get_clipboard_text
    from utilities import  clean_tsv



class ClipBrowser(App):
    """This class implements the `App` class from `textual`. It defines the layout of the Terminal 
    User Interface (TUI).  

    Attributes:
        text (str): Store the text available in all the application, this text is usually 
            updated with data contained in the clipboard.
        parser (clipParser): A text parser that parse text to extract valuable data (thanks to `userTypeParser`) 
            and execute action based on the data extracted (thanks to `userAction`).
        active_tab (str): Name of the currently active tab
        
    
    """
    APP_TITLE = "📝CyberClip👩‍💻"
    CSS_PATH = "app.scss"
    COMMANDS = App.COMMANDS | {ActionCommands}
    BINDINGS = [
        ("ctrl+s", "save", "Save actual view."),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+f", "select_action_filter", "Filter"),
        ("ctrl+b", "copy", "Copy actual content to clipboard."),
        Binding("ctrl+r", "reset", "Reset content view to clipboard content.", False),
    ]
    CLOSE_TIMEOUT = None

    orange_theme =  Theme(
        name="orange",
        primary="#f16e00",
        secondary="#ffb4e6",
        warning="#ffcc00",
        error="#ba3c5b",
        success="#50be87",
        accent="#a885d8",
        foreground="#cdd6f4",
        background="#000000",
        surface="#181512",
        panel="#201d1b",
        variables={
            "block-cursor-background":"#f16e00",
            "footer-key-foreground": "#f16e00",
        })

    orange_theme_light =  Theme(
        name="orange-light",
        primary="#f16e00",
        secondary="#ffb4e6",
        warning="#ffcc00",
        error="#ba3c5b",
        success="#50be87",
        accent="#a885d8",
        foreground="#160b01",
        background="#E4DCD0",
        surface="#F0E3D3",
        panel="#EECEA5",
        dark=False,
        variables={
            "block-cursor-background":"#f16e00",
            "footer-key-foreground": "#f16e00",
        })

    parser = var(clipParser())
    recipe_parser = var(clipParser())
    #graph = var(nx.DiGraph())
    active_node = var({})
    text = reactive("Waiting for Update...", init=False)
    active_tab : str = ""
    try:
        file = Path(__file__).parent / 'data/recipes.yml'
        if not file.exists():
            file.write_text("[]")
        with open(Path(__file__).parent / 'data/recipes.yml', "r", encoding="utf8") as f:
            recipes = var([Recipe(recipe_dict=i) for i in yaml.safe_load(f.read())])
    except Exception as e:
        recipes = var([])
        print("Error loading recipes...", e)

    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)
        if self.is_web:
            self.COMMAND_PALETTE_BINDING = "ctrl+j"
        self.actions = []

    async def on_mount(self):
        self.parser.load_all()
        self.recipe_parser.load_all()
        self.notify(f"Loaded parsers: {len(self.parser.parsers.keys())}\nLoaded actions: {len(self.parser.actions.keys())}")

    def compose(self) -> ComposeResult:
        """Compose the main UI. Generate three tabs corresponding to the three modes of the application :
        
        - Main view which displays the content of keyboard, parser extractors on left and actions on right.
        - Table view for sorting and filtering results of action or to enrich tabular data/files.
        - Rules view for managing rules to apply to data (chains of actions with defined parameters), 
        the rules became new actions available in the command pallette. 

        Warning: 
            Table and rule views are a WIP.

        """
        self.console.set_window_title(ClipBrowser.APP_TITLE)
        with TabbedContent(id="maintabs"):
            with TabPane(ClipBrowser.APP_TITLE, id="clipview"):
                yield Grid(
                    DataLoader(id="left-pannel"),
                    ContentView(id="content-view"),
                    ActionPannel(id="action-pannel"),
                    id="maingrid"
                )
            with TabPane('Table View', id="tableview"):
                yield FiltrableDataFrame(pd.DataFrame(), id="main-table")
            with TabPane('Recipes', id="recipes"):
                yield RecipesPannel()
            # with TabPane("Graph View", id="graphview"):
            #     yield GraphPannel()
        yield Footer()
        self.register_theme(self.orange_theme)
        self.register_theme(self.orange_theme_light)

    def action_quit(self):
        sys.exit()

    def action_save(self):      
        with open("clipboard.txt", "w") as f:
            f.write(self.text)
            self.deliver_text(f, encoding="utf-8")

    def action_copy(self):
        self.copy_to_clipboard(self.text)
        self.notify("Copied in clipboard!")

    def action_reset(self):
        self.text = get_clipboard_text()

    def action_select_action_filter(self):
        filter = self.query_one("#action-filter").focus()
        filter.value = ""

    @property
    def contentview(self):
        return self.query_one(ContentView)

    @on(TabbedContent.TabActivated)
    def check_TSV(self, event: TabbedContent.TabActivated):
        self.active_tab = event.tab.label_text
        if self.active_tab == "Table View":
            df = pd.DataFrame()
            parser = TSVParser.tsvParser(self.text)
            if parser.extract():            
                try:
                    df = pd.read_csv(StringIO(self.text), sep="\t", header=None, skip_blank_lines=False)
                    df.columns = [str(i) for i in df.columns]
                    self.call_after_refresh(self.update_dataframe, df)
                except Exception as e:
                    self.notify(f"Error : {str(e)}" ,title="Error while loading data...", timeout=5, severity="error")
        if self.active_tab == ClipBrowser.APP_TITLE:
            self.parser.parseData(self.text)
        if self.active_tab == "Recipes":
            self.query_one(RecipesPannel).refresh_recipes()
            if querybuttons:= self.query(RecipeButton):
                querybuttons[0].press()
        if self.active_tab == "Graph View":
            self.query_one(GraphPannel).refresh(recompose=True)

    async def update_dataframe(self, df):
        tab = self.query_one("#tableview")
        await tab.remove_children()
        tab.mount(FiltrableDataFrame(pd.DataFrame(df), id="main-table"))

    def watch_text(self, new_text: str) -> None:
        if self.text or self.text == "":
            self.parser.parseData(self.text)
            self.contentview.update_text(new_text, force=True)
            if self.active_tab == ClipBrowser.APP_TITLE:
                self.query_one(ActionPannel).filter_action()

    @work()
    async def get_param(self, actionnable: actionInterface | ParserInterface):
        if isinstance(actionnable, ParserInterface) or not actionnable.complex_param :
            await self.handle_param(actionnable)
        else:
            param_screen = ParamScreen()
            param_screen.border_title = f"Parameters for '{actionnable.description}' action."
            param_screen.actionnable = actionnable
            try:
                self.push_screen(param_screen, callback=partial(self.handle_param, actionnable))
            except:
                self.notify(f"Error while executing action : {traceback.format_exc()}", severity="error")

    async def handle_param(self, actionnable : actionInterface | ParserInterface ,  complex_param : dict | None = None, recipe_parser : bool = False):
        if complex_param :
            actionnable.complex_param = complex_param

        if self.active_tab == ClipBrowser.APP_TITLE:
            try:
                self.text = await self.parser.apply_actionable(actionnable, self.query_one(TextArea).text)

                # # Add executed action to graph view
                # previous_node = self.active_node
                # _node = {
                #         "label": actionnable.description, 
                #         "supported":actionnable.supportedType,
                #         "params":actionnable.complex_param
                #         }
                # action_node = add_node(self.graph, _node, "action", previous_node)
                # text_node = {"text":self.text, "detected":self.parser.detectedType}
                # self.active_node = add_node(self.graph, text_node, "text", action_node)
                # if not self.graph.get_edge_data(previous_node.get("id"),action_node.get("id")):
                #     self.graph.add_edge(previous_node.get("id"), action_node.get("id"))
                #     self.graph.add_edge(action_node.get("id"), self.active_node.get("id"))

            except Exception as e:
                self.notify("Error applying action..." + str(e) + traceback.format_exc(), severity="error")  
        elif self.active_tab == "Table View":
            dataframe = self.query_one(FiltrableDataFrame)
            column_name = dataframe.datatable.df.columns[dataframe.datatable.cursor_column]
            new_column_name = dataframe.datatable.get_column_name(f"{actionnable.__class__.__name__}_{column_name}")
            try:
                if recipe_parser:
                    dataframe.datatable.df[new_column_name] = await asyncio.gather(*(self.recipe_parser.apply_actionable(actionnable, str(text)) for text in dataframe.datatable.df[column_name]))
                    dataframe.datatable.df[new_column_name] = dataframe.datatable.df.apply(lambda x: clean_tsv(x[new_column_name], x[column_name]), axis=1)
                    dataframe.datatable.update_displayed_df(dataframe.datatable.df)
                else:
                    dataframe.datatable.df[new_column_name] = await asyncio.gather(*(self.parser.apply_actionable(actionnable, str(text)) for text in dataframe.datatable.df[column_name]))
                    dataframe.datatable.df[new_column_name] = dataframe.datatable.df.apply(lambda x: clean_tsv(x[new_column_name], x[column_name]), axis=1)
                    dataframe.datatable.update_displayed_df(dataframe.datatable.df)
            except Exception as e:
                self.notify("Error executing an action..." + str(e) + traceback.format_exc(), severity="error")




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w","--web", help="Serve as a web app", action="store_true")
    parser.add_argument("-d","--docker", help="Serve in a docker container", action="store_true")
    args = parser.parse_args()
    path = Path(__file__)
    if args.web:
        from textual_serve.server import Server
        server = Server(f"python {path}")
        server.serve()
    elif args.docker:
        from textual_serve.server import Server
        server = Server(f"python {path}", host="0.0.0.0")
        server.serve()
    else:
        cyberClip = ClipBrowser()
        cyberClip.run()

if __name__ == "__main__":
    main()
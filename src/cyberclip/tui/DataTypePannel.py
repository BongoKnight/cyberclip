import pyperclip
from rich.console import RenderableType
from textual.reactive import var
from textual.containers import  VerticalScroll, Horizontal, Vertical
from textual.widgets import Static,  Button, Switch, TextArea
from textual.app import ComposeResult


try:
    from cyberclip.clipboardHandler import get_clipboard_text
except:
    from clipboardHandler import get_clipboard_text

class DataTypeButton(Static):
    """A dataType widget to extract and handle actions on one specific types of data."""
    DEFAULT_CSS = """
"""
    parser_type = var("text")

    def __init__(self, active: bool = True, content: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        super().__init__(content, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self._active = active
        self.parser_type = str(content)

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataType.""" 
        yield Horizontal(
             Button(self.parser_type, id="datatype-button", classes=""),
             Switch(value=self._active, id="datatype-active"), classes="datatype"
             )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        if event.button.id == "datatype-button":
            from tui.ContentView import ContentView
            contentView = self.parent.ancestors[-1].query_one(ContentView)
            if contentView:
                self.app.text = "\n".join(self.app.parser.results["matches"].get(self.parser_type, ""))
                results = self.app.parser.results["matches"].get(self.parser_type, [])
                
                # # Add data to investigation graph
                # previous_node = self.app.active_node
                # parser_node = add_node(self.app.graph, {"label": self.parser_type, "detected":results}, "parser")
                # text_node = {"text":self.app.text, "detected":self.app.parser.detectedType}
                # self.app.active_node = add_node(self.app.graph, text_node, "text", parser_node)
                # if self.parser_type !="text" and not self.app.graph.get_edge_data(previous_node.get("id"),parser_node.get("id")):
                #     self.app.graph.add_edge(previous_node.get("id"), parser_node.get("id"))
                #     self.app.graph.add_edge(parser_node.get("id"), self.app.active_node.get("id"))
                contentView.filter_action()
    
    @property
    def switch(self) -> Switch:
        try:
            return self.query_one(Switch)
        except:
            return


    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Event handler called when Switch is pressed."""
        from tui.ContentView import ContentView
        contentView = self.parent.ancestors[-1].query_one(ContentView)
        contentView.filter_action()

class DataLoader(Static):
    """A dataLoader widget."""
    select_all_datatype = var(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        from tui.ContentView import ContentView
        textArea = self.app.contentview.query_one(TextArea)
        if event.button.id == "update-button":
            self.app.text = get_clipboard_text()
            # graph_node = {"text":self.app.text,
            #               "detected":self.app.parser.detectedType
            #               }
            # self.app.active_node = add_node(self.app.graph, graph_node, "text")
        if event.button.id == "text-update-button":
            self.app.text = textArea.text
            # graph_node = {
            #             "detected":self.app.parser.detectedType,
            #             "text":self.app.text
            #              }
            # self.app.active_node = add_node(self.app.graph, graph_node, "text")
        if event.button.id == "filter-button":
            self.select_all_datatype = not  self.select_all_datatype 
            for switch in self.query(Switch):
                switch.value = self.select_all_datatype

    def add_dataType(self, type_of_data: str, active : bool = True) -> DataTypeButton:
        """An action to add a timer."""
        new_datatype = DataTypeButton(content=type_of_data, classes="datatype", active=active)
        self.query_one("#data-type-container").mount(new_datatype)
        new_datatype.scroll_visible()
        new_datatype.parser_type = type_of_data 
        return new_datatype

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader."""
        if not self.app.is_web:
            yield Button("Parse clip", id="update-button", variant="success") 
        yield Button("Parse text", id="text-update-button", variant="primary")
        yield VerticalScroll(id="data-type-container")
        yield Button("(Un)select all", id="filter-button", variant="primary")
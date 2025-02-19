import networkx as nx
import json

from rich import print
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from textual import on, work
from textual.app import App
from textual.screen import ModalScreen
from textual.message import Message
from textual.reactive import var, reactive
from textual.containers import  Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Button, Input, Label, TextArea, Switch, Select
from textual.app import ComposeResult

from netext.textual_widget.widget import GraphView
from netext import EdgeRoutingMode, EdgeSegmentDrawingMode, ArrowTip, ConsoleGraph, EdgeProperties




def print_node(node_name, node, style):
    _type = node.get("type","")
    if _type == "parser":
        label, detected = node.get("label",""), node.get("detected",[])
        t = Table(title="[italic green]Parser[/]",style="green", width=30)
        t.add_column("Key")
        t.add_column("Value")
        t.add_row("type", Text(label))
        t.add_row("detected", Text(str(len(detected))))
    
    elif _type == "text":
        label, detected = node.get("label",""), node.get("detected",[])
        t = Table(style="magenta", width=40)
        t.add_column("Key")
        t.add_column("Value")
        t.add_row("text", Text(label))
        t.add_row("detected", Text(", ".join([f"{_type}" for _type in detected])))

    elif _type == "action":
        label, supported = node.get("label"), node.get("supported")
        t = Table(title="[italic blue]Action[/]", style="blue", width=30)
        t.add_column("Key")
        t.add_column("Value")
        t.add_row("Name", label)
        t.add_row("On", Text(", ".join([f"{_type}" for _type in supported])))
    
    else:
        t = Text(node_name)
    return t



class GraphPannel(Static):
    DEFAULT_CSS = """
    GraphView {
        width: 1fr;
        height: 1fr;
    }"""


    def compose(self) -> ComposeResult:
        nx.set_edge_attributes(self.app.graph, EdgeSegmentDrawingMode.BOX, "$edge-segment-drawing-mode")
        nx.set_edge_attributes(self.app.graph, EdgeRoutingMode.ORTHOGONAL, "$edge-routing-mode")
        nx.set_edge_attributes(self.app.graph, ArrowTip.ARROW, "$end-arrow-tip")
        nx.set_node_attributes(self.app.graph, print_node, "$content-renderer")
        yield GraphView(self.app.graph)

    @on(GraphView.ElementClick)
    def copy_text(self, event: GraphView.ElementClick):
        node = self.app.graph.nodes.get(event.element_reference.ref)
        if node and node.get("type") == "text" and (text:=node.get("text")):
            self.app.copy_to_clipboard(text)
            self.notify("Text copied to clipboard!")
        if node and node.get("type") == "action" and (params:=node.get("params")):
            self.app.copy_to_clipboard(json.dumps(params,indent=4))
            self.notify("Params copied to clipboard!")
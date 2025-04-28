from __future__ import annotations
from textual.app import ComposeResult
from textual import on
from textual.reactive import reactive, var
from textual.widgets import Static, Tree, tree
import re
import json

try:
    from .TagsInput import TagsInput, Tag
except:
    from cyberclip.tui.TagsInput import TagsInput, Tag



def get_path(node: tree.TreeNode):
    clean_path = str(node.label)
    if clean_path == '{} ':
        clean_path = ""
    elif clean_path == '[] ':
        clean_path = ".[]"
    elif match := re.search(r"\[\] (?P<arraykey>.*)", clean_path):
        clean_path = '"' + match.group("arraykey") + '"' + '[]'
    elif match := re.search(r"\{\} (?P<dictkey>.*)", clean_path):
        clean_path = '"' + match.group("dictkey") + '"'
    elif match := re.search(r"^(?P<leafkey>.*)=", clean_path):
        clean_path = '"' + match.group("leafkey") +'"'
    else:
        clean_path = ""
    if node and node.parent:
        if str(node.parent.label).startswith("[]"):
            if not node.children:
                # Add array index for leaf key 
                return get_path(node.parent)[:-2] + f'[{clean_path.replace('"',"")}]'
            else:
                return get_path(node.parent)
        else:
            return get_path(node.parent) + f'.{clean_path}'
    else:
        return clean_path

class CustomTree(Tree):
    highlighted_nodes = reactive(set[tree.TreeNode])
    
    @on(Tree.NodeSelected)
    def switch_state(self, event: Tree.NodeSelected):
        event.prevent_default()
        event._stop_propagation = True
        if event.node in self.highlighted_nodes:
            self.highlighted_nodes.remove(event.node)
        else:
            self.highlighted_nodes.add(event.node)
        self.watch_highlighted_nodes()


    def watch_highlighted_nodes(self):
        if isinstance(self.parent, SimpleJSONInput):
            self.parent.query_one(TagsInput)._value = set(self.selected_paths + list(self.parent.query_one(TagsInput)._value))


    @property
    def selected_paths(self):
        return [get_path(node) for node in self.highlighted_nodes]

class SimpleJSONInput(Static):
    json_scheme = reactive("") 
    label = var("")
    _value = var(list[str], init=False)
    def __init__(self, label : str ="", value : list[str] = [], json_scheme: str = "", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self._value = value
        self.json_scheme = json_scheme

    def compose(self) -> ComposeResult:
        yield TagsInput(label=self.label, value=set(self._value))
        yield CustomTree("Select fields to return")

    @on(Tag.Deleted)
    def delete_value(self, event: Tag.Deleted):
        tree_widget = self.query_one(CustomTree)
        if event.value in tree_widget.selected_paths:
            for node in tree_widget.highlighted_nodes.copy():
                if event.value == get_path(node):
                    tree_widget.highlighted_nodes.remove(node)

    @property
    def value(self):
        return list(self.query_one(TagsInput)._value)
    
    @value.setter
    def value(self, value:list[str] = []):
        if self.is_mounted:
            tags = self.query_one(TagsInput)
            tags._value = value



    def on_mount(self):
        tree = self.query_one(CustomTree)
        tree.add_json(json.loads(self.json_scheme), tree.root)
        tree.root.expand_all()
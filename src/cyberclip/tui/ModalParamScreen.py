from copy import deepcopy

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Markdown, Collapsible
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import var


try:
    from cyberclip.tui.TagsInput import TagsInput
    from cyberclip.tui.JSONSelector import SimpleJSONInput
    from cyberclip.tui.SimpleInput import SimpleInput, SimpleSelect, SimpleTextArea
    from cyberclip.tui.FileInput import FileInput
    from cyberclip.tui.SelectionInput import SelectionInput
    from cyberclip.tui.MultiSelect import MultiSelect
    from cyberclip.userAction import actionInterface
except:
    from tui.TagsInput import TagsInput
    from tui.JSONSelector import SimpleJSONInput
    from tui.FileInput import FileInput
    from tui.SimpleInput import SimpleInput, SimpleSelect, SimpleTextArea
    from tui.SelectionInput import SelectionInput
    from tui.MultiSelect import MultiSelect
    from userAction import actionInterface

class ParamScreen(Screen):
    """Modal screen for entering parameters"""
    DEFAULT_CSS = """
    ParamScreen {
        align: center middle;
        background: black 30%;
        layout: vertical;
    }
    #dialog {
        padding: 3 3;
        width: 80%;
        height: 80%;
        border: $primary;
        }

    #fulldesc{
        border: $primary;
        width: 100%;
        height: 12;
    }
    
    #submit {
        height: 3;
        align-horizontal: right;
    }
    """

    actionnable : actionInterface = var(None)
    BINDINGS = [("escape", "app.pop_screen", "Escape config screen."),("ctrl+s", "submit", "Submit")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Collapsible(Markdown("", id="fulldesc"), title="Help"),
            VerticalScroll(*self.get_complex_param_widgets()),
            Horizontal(
                Button("Save params", variant="primary", id="save"),
                Button("Cancel", variant="error", id="cancel"), id="submit"
            ),
            id="dialog"
        )

    def on_mount(self) -> None:
        self.query_one("#dialog").border_title = self.actionnable.description
        self.query_one("#fulldesc", Markdown).update(self.actionnable.__doc__)

    def action_submit(self) -> None:
        self.dismiss(result=self.return_parameters())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "save":
            self.dismiss(result=self.return_parameters())
            
    def return_parameters(self):
        params = {}
        for widget in self.query(".complex-input"):
            key = widget.label
            value = widget.value
            if isinstance(widget, SimpleInput):
                params.update({key: {"value":value, "type":"text"}})
            if isinstance(widget, SimpleTextArea):
                params.update({key: {"value":value, "type":"longtext"}})
            if isinstance(widget, SimpleSelect):
                params.update({key: {"value":value, "type":"list", "choices":widget.choices}})
            if isinstance(widget, FileInput):
                params.update({key: {"value":value, "type":"filename"}})
            if isinstance(widget, TagsInput):
                params.update({key: {"value":value, "type":"tags"}})
            if isinstance(widget, SelectionInput):
                params.update({key: {"value":value, "type":"fixedlist", "choices": widget.choices}})
            if isinstance(widget, MultiSelect):
                params.update({key: {"value":value, "type":"compactlist", "choices": widget.options}})
            if isinstance(widget, Checkbox):
                params.update({str(widget.label): {"value":value, "type":"bool"}})
            if isinstance(widget, SimpleJSONInput):
                params.update({str(widget.label): {"value":value, "type":"jsonpath","scheme":widget.json_scheme}})
        return params

    def get_complex_param_widgets(self):
        widgets = []
        if self.actionnable.complex_param:
            params = deepcopy(self.actionnable.complex_param)
            for key, value in params.items():
                stored_values = self.actionnable.get_param_value(key)
                if isinstance(value, dict):                
                    default_value = value.get("default", [])
                    options = value.get("choices", [])
                    assert "type" in value.keys()
                    assert "value" in value.keys()
                    input_type = value.get("type", str)
                    if input_type.lower() == "text":
                        widgets.append(SimpleInput(label=key, value=stored_values, classes="complex-input"))
                    elif input_type.lower() == "longtext":
                        widgets.append(SimpleTextArea(label=key, value=stored_values, classes="complex-input"))
                    elif input_type.lower() == "tags":
                        widgets.append(TagsInput(label=key, value=stored_values, classes="complex-input"))
                    elif input_type.lower() in ["filename","dir","filesave","save","fileopen"]:
                        widgets.append(FileInput(label=key, value=stored_values, type=input_type.lower(), classes="complex-input"))
                    elif input_type.lower() == "list":
                        widgets.append(SimpleSelect(label=key, value=stored_values, choices=options, classes="complex-input"))
                    elif input_type.lower() == "fixedlist":
                        widgets.append(SelectionInput(label=key, value=stored_values, choices=options, classes="complex-input"))
                    elif input_type.lower() == "compactlist":
                        widgets.append(MultiSelect(label=key, options=options, classes="complex-input"))
                    elif input_type.lower() == "bool" or input_type.lower() == "boolean":
                        widgets.append(Checkbox(label=key, value=stored_values, classes="complex-input"))
                    elif input_type.lower() == "json" or input_type.lower() == "jsonpath":
                        json_scheme = ""
                        if json_parser := self.app.parser.parsers.get("json"):
                            json_scheme = json_parser.extract()[0]
                        widgets.append(SimpleJSONInput(label=key, value=stored_values, json_scheme=json_scheme ,classes="complex-input"))
                if isinstance(value, str) and len(value)<100:
                    widgets.append(SimpleInput(label=key, value=stored_values, classes="complex-input"))
                    self.actionnable.complex_param.update({key:{"type":"text","value":stored_values}})
                elif isinstance(value, str) and len(value)>=100:
                    widgets.append(SimpleTextArea(label=key, value=stored_values, classes="complex-input"))
                    self.actionnable.complex_param.update({key:{"type":"longtext","value":stored_values}})
                if isinstance(value,list):
                    if len(value) == 0:
                        widgets.append(TagsInput(label=key, value=stored_values, classes="complex-input"))
                        self.actionnable.complex_param.update({key:{"type":"tags","value":stored_values}})
                    else:
                        widgets.append(SelectionInput(label=key, choices=stored_values, classes="complex-input"))
                        self.actionnable.complex_param.update({key:{"type":"fixedlist","value":stored_values}})
                if isinstance(value, bool):
                    widgets.append(Checkbox(label=key, value=value))
                    self.actionnable.complex_param.update({key:{"type":"bool","value":stored_values}})
        return widgets
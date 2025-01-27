from copy import deepcopy

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, Input, Checkbox
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import var


try:
    from cyberclip.tui.ActionPannel import ActionButton
    from cyberclip.tui.TagsInput import TagsInput
    from cyberclip.tui.SimpleInput import SimpleInput, SimpleSelect
    from cyberclip.tui.FileInput import FileInput
    from cyberclip.tui.SelectionInput import SelectionInput
    from cyberclip.tui.MultiSelect import MultiSelect
    from cyberclip.userAction import actionInterface
except:
    from tui.ActionPannel import ActionButton
    from tui.TagsInput import TagsInput
    from tui.FileInput import FileInput
    from tui.SimpleInput import SimpleInput, SimpleSelect
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
    
    #submit {
        height: 3;
        align-horizontal: right;
    }
    """

    action : actionInterface = var(None)
    BINDINGS = [("escape", "app.pop_screen", "Escape config screen."),("ctrl+s", "submit", "Submit")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            VerticalScroll(*self.get_complex_param_widgets()),
            Horizontal(
                Button("Save params", variant="primary", id="save"),
                Button("Cancel", variant="error", id="cancel"), id="submit"
            ),
            id="dialog"
        )

    def on_mount(self) -> None:
        self.query_one("#dialog").border_title = self.action.description

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
        return params

    def get_complex_param_widgets(self):
        widgets = []
        if self.action.complex_param:
            params = deepcopy(self.action.complex_param)
            for key, value in params.items():
                stored_values = self.action.get_param_value(key)
                if isinstance(value, dict):                
                    default_value = value.get("default", [])
                    options = value.get("choices", [])
                    assert "type" in value.keys()
                    assert "value" in value.keys()
                    input_type = value.get("type")
                    if input_type.lower() == "text":
                        widgets.append(SimpleInput(label=key, value=stored_values, classes="complex-input"))
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
                if isinstance(value, str):
                    widgets.append(SimpleInput(label=key, value=stored_values, classes="complex-input"))
                    self.action.complex_param.update({key:{"type":"text","value":stored_values}})
                if isinstance(value,list):
                    if len(value) == 0:
                        widgets.append(TagsInput(label=key, value=stored_values, classes="complex-input"))
                        self.action.complex_param.update({key:{"type":"tags","value":stored_values}})
                    else:
                        widgets.append(SelectionInput(label=key, choices=stored_values, classes="complex-input"))
                        self.action.complex_param.update({key:{"type":"fixedlist","value":stored_values}})
                if isinstance(value, bool):
                    widgets.append(Checkbox(label=key, value=value))
                    self.action.complex_param.update({key:{"type":"bool","value":stored_values}})
        return widgets
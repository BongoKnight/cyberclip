import yaml
from yaml.loader import SafeLoader
from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal
from textual.reactive import var, reactive
from textual.widgets import Footer, Static, Input
from pathlib import Path
from rich.markdown import Markdown

class ConfigScreen(Screen):
    DEFAULT_CSS = """ConfigScreen{
        layout: vertical
    }

    ConfigInput {
        height: 3;
    }

    #conf-name{
        width: 20;
    }
    #conf-input{
        min-width: 50%;
        width: auto;
    }"""
    BINDINGS = [("escape", "app.pop_screen", "Escape config screen."),
                ("ctrl+s", "save_conf", "Save config")]

    def compose(self) -> ComposeResult:
        config_fields = {}
        try:
            with open(Path(__file__).parent / '../data/conf.yml', encoding="utf8") as f:
                config_fields = yaml.load(f, Loader=SafeLoader)
            for config_name, config_elems in config_fields.items():
                yield Static(Markdown(f"# {config_name}"))
                for config in config_elems:
                    if isinstance(config, dict):
                        for key, value in config.items():
                            widget = ConfigInput()
                            widget.input_name = key
                            widget.input_value = value
                            widget.parent_conf = config_name
                            yield widget
        except Exception as e:
            self.app.notify("The file conf.yaml might not exist. Error : {e}", title="Error with conf.", timeout=5, severity="error")
        yield Footer()

    def action_save_conf(self):
        inputs = self.query(ConfigInput)
        conf = {}
        for input in inputs:
            if conf.get(input.parent_conf):
                conf[input.parent_conf].append({input.input_name:input.input_value})
            else:
                conf[input.parent_conf] = [{input.input_name:input.query_one(Input).value}]
        with open(Path(__file__).parent / '../data/conf.yml', "w", encoding="utf8") as f:
            config_fields = yaml.dump(conf, f)


class ConfigInput(Static):

    parent_conf = var("")
    input_name = var("")
    input_value = reactive("")
    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Horizontal(
            Static(self.input_name, id="conf-name"),
            Input(value=self.input_value, id="conf-input")
            )

if __name__=='__main__':
    class ConfigApp(App):
         def compose(self) -> ComposeResult:
            yield ConfigScreen()
            yield Footer()
    app = ConfigApp()
    app.run()
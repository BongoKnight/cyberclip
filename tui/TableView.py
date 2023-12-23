from textual.events import Mount
from dataclasses import dataclass
from textual.widgets import DataTable, Input, Label, Log, RadioButton, RadioSet, Button, Static, Checkbox
from textual.containers import Horizontal, ScrollableContainer
import pandas as pd
from pathlib import Path
import re
import pyperclip
from textual.app import ComposeResult
from textual import on
from textual.app import App

#####################
#  Helping methods  #
#####################

def match_value(string, regex):
    if regex == '' :
        return True
    try:
        match = True if re.search(regex, string) else False
        return match
    except:
        return False

#####################
#  Helping classes  #
#####################

@dataclass
class DataFrameFilter:
    column_index: int
    value: str
    exclude: bool = False

type DataFrameFilters = list[DataFrameFilter]


#####################
#      Widgets      #
#####################

class FilterInput(Static):

    DEFAULT_CSS = """
    FilterInput > Input {
        height: 1;
        margin: 0;
        padding: 0;
        border: none;
    }
    FilterInput > Input:focus {
        height: 1;
        margin: 0;
        padding: 0;
        border: none;
    }
    Checkbox {
        margin: 0;
        padding: 0;
        border: none;
    }
    Checkbox:focus {
        margin: 0;
        padding: 0;
        border: none;
    }
    FilterInput{
        layout: horizontal;
        width: auto;
    }
    """
    def __init__(self, input_id=0):
        super().__init__()
        self.input_id = input_id

    def compose(self) -> ComposeResult:
        yield Input(id=f"filter-input-{self.input_id}",  classes="filter-input", placeholder="Filter...")
        yield Checkbox(classes="reverse")

from textual.widgets import DataTable
import pandas as pd


class DataFrameTable(DataTable):
    """Display Pandas dataframe in DataTable widget."""

    def __init__(self, dataframe = pd.DataFrame()):
        super().__init__()
        self.df = dataframe
        self.showed_df = dataframe
        self.add_df(dataframe)
        self.sort_ascending = {}

    def add_df(self, df: pd.DataFrame):
        """Add DataFrame data to DataTable."""
        self.showed_df = df
        self.add_columns(*self._add_df_columns())
        self.add_rows(self._add_df_rows()[0:])
        return self

    def update_df(self, df: pd.DataFrame):
        """Update DataFrameTable with a new DataFrame."""
        # Clear existing datatable
        self.clear(columns=True)
        # Redraw table with new dataframe
        self.add_df(df)

    def _add_df_rows(self) -> None:
        return self._get_df_rows()

    def _add_df_columns(self) -> None:
        return self._get_df_columns()

    def _get_df_rows(self) -> list[tuple]:
        """Convert dataframe rows to iterable."""
        return list(self.showed_df.itertuples(index=False, name=None))

    def _get_df_columns(self) -> tuple:
        """Extract column names from dataframe."""
        return tuple(self.showed_df.columns.values.tolist())
    
    @on(DataTable.HeaderSelected)
    def sort_table(self, event : DataTable.HeaderSelected):
        column_name = self.showed_df.columns[event.column_index]
        self.sort_ascending[column_name] = not self.sort_ascending.get(column_name, False)
        sort_order = self.sort_ascending[column_name]
        self.showed_df = self.showed_df.sort_values(by=column_name, ascending = sort_order)
        self.update_df(self.showed_df)

    def filter_table(self, filters : DataFrameFilters):
        df = self.df
        for filter in filters :
            column_name = self.showed_df.columns[filter.column_index]
            if filter.exclude:
                df = df[df.apply(lambda row: match_value(str(row[column_name]), filter.value), axis=1) == False]
            else:
                df = df[df.apply(lambda row: match_value(str(row[column_name]), filter.value), axis=1) == True]
        self.update_df(df)

class FiltrableDataFrame(Static):
    DEFAULT_CSS = """
    FiltrableDataFrame {
        height: 99%;
        scrollbar-gutter: stable;
        layout: grid;
        grid-size: 1 3;  /* 3 lines */
        grid-columns: 1fr;
        grid-rows: 5 3 1fr;
    }
    #table-option{
        row-span: 1;
    }
    #table-container{
        row-span: 2;
        overflow-x: scroll;
        overflow-y: hidden;
        width: auto;
        height: auto;
    }

    #filter-container{
        width: auto;
        margin-top: 1;
        margin-bottom: 1;
    }

    #selectmode{
        border-title-color: white;
    }

    DataFrameTable{
        height: auto;
        width: auto;
        row-span: 1;
        overflow: hidden scroll;
    }

    #copy, #copy-table, #clean-filter {
        margin-top: 1
    }
    """
    

    def __init__(self, df, **kwargs):
        super().__init__(**kwargs)
        self.datatable = DataFrameTable(df)
        self.datatable.cursor_type = "cell"
        
    def on_mount(self):
        self.watch(self.datatable, "virtual_size", self.update_input_size, init=True)

    def compose(self) -> ComposeResult:
        with Horizontal(id="table-option"):
            with RadioSet(id="selectmode") as f:
                    yield RadioButton("cell", value=True)
                    yield RadioButton("row")
                    yield RadioButton("column")
                    f.border_title = "Select :"
            yield Button("Copy selected",id="copy", variant="primary")
            yield Button("Copy table",id="copy-table", variant="primary")
            yield Button("Clean filters",id="clean-filter", variant="error")
        with ScrollableContainer(id="table-container"):
            yield Horizontal(*[FilterInput(i) for i in range(len(self.datatable.showed_df.columns)) ], id="filter-container")
            yield self.datatable
    
    def filter_columns(self):
        df = self.datatable.df
        filters = []
        for input in self.query(FilterInput):
            input_field = input.query_one(Input)
            reverse_search = input.query_one(Checkbox).value
            column_index = int(input_field.id.split("-")[-1])
            filters.append(DataFrameFilter(column_index, input_field.value, reverse_search))
        self.datatable.filter_table(filters)
        

    @on(Input.Changed)
    def update_on_input(self):
        self.filter_columns()

    @on(Checkbox.Changed)
    def update_on_checkbox(self):
        self.filter_columns()

    @on(RadioSet.Changed, "#selectmode")
    def change_selection_mode(self, event: RadioSet.Changed):
        self.datatable.cursor_type = str(event.pressed.label)
        
    @on(Button.Pressed, "#copy")
    def copy_selected_to_clipboard(self):
        if self.datatable.cursor_type == "cell":
            cell = self.datatable.get_cell_at(self.datatable.cursor_coordinate)
            pyperclip.copy(str(cell))
        elif self.datatable.cursor_type == "row":
            row = self.datatable.get_row_at(self.datatable.cursor_coordinate.row)
            pyperclip.copy("\t".join([str(i) for i in row]))
        elif self.datatable.cursor_type == "column":
            column = self.datatable.get_column_at(self.datatable.cursor_coordinate.column)
            pyperclip.copy("\n".join([str(i) for i in column]))

    @on(Button.Pressed, "#copy-table")
    def copy_table_to_clipboard(self):
        pyperclip.copy(self.datatable.showed_df.to_csv(sep="\t",index=False))

    @on(Button.Pressed, "#clean-filter")
    def copy_table_to_clipboard(self):
        for input in self.query(FilterInput):
            input_field = input.query_one(Input)
            reverse_search = input.query_one(Checkbox)
            input_field.value = ''
            reverse_search.value = False

    def update_input_size(self):
        for column in self.datatable.columns.values() :
            self.query_one(f"#filter-input-{str(self.datatable.get_column_index(column.key))}").styles.width = column.content_width - 1
            




if __name__ == "__main__":

    df = pd.read_csv(Path(__file__).parent / "../data/ows.csv", sep=";")

    class ClassApp(App):
        def compose(self):
            yield Static(
                id="instruction_label",
            )
            yield FiltrableDataFrame(df)
    app = ClassApp()
    app.run()

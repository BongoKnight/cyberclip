from textual.events import Mount
from dataclasses import dataclass
from textual.widgets import DataTable, Input, Label, Log, RadioButton, RadioSet, Button, Static, Checkbox, Select
from textual.containers import Horizontal, Vertical, ScrollableContainer
from cyberclip.tui.MultiSelect import MultiSelect
import pandas as pd
from pathlib import Path
from typing import TypeAlias
from textual.reactive import reactive
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

DataFrameFilters : TypeAlias = list[DataFrameFilter]


#####################
#      Widgets      #
#####################

class FilterInput(Static):
    """
    Small input field with a checkbox for indicating a reverse filter.
    """

    DEFAULT_CSS = """
    FilterInput > Input {
        height: 1;
        margin: 0;
        padding: 0;
        border: none;
        width: 1fr;
    }
    FilterInput > Input:focus {
        height: 1;
        margin: 0;
        padding: 0;
        border: none;
        width: 1fr;
    }
    Checkbox {
        margin: 0;
        padding: 0;
        border: none;
        width: auto;
    }
    Checkbox:focus {
        margin: 0;
        padding: 0;
        border: none;
        width: auto;
    }
    FilterInput{
        layout: horizontal;
        width: auto;
    }
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_mout(self):
        self.query_one(Checkbox).tooltip = "Exclude matches"

    def compose(self) -> ComposeResult:
        yield Input(classes="filter-input", placeholder="Filter...")
        yield Checkbox(classes="reverse")

    @property
    def input(self):
        return self.query_one(Input)
    
    @property
    def checkbox(self):
        return self.query_one(Checkbox)

from textual.widgets import DataTable
import pandas as pd


class DataFrameTable(DataTable):
    """Display Pandas dataframe in DataTable widget."""
    def __init__(self, dataframe = pd.DataFrame()):
        super().__init__()
        self.df = dataframe
        self.displayed_df = dataframe
        self.add_df(dataframe)
        self.sort_ascending = {}

    def add_df(self, df: pd.DataFrame, replace_df = True):
        """Add DataFrame data to DataTable."""
        self.displayed_df = df
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
        return list(self.displayed_df.itertuples(index=False, name=None))

    def _get_df_columns(self) -> tuple:
        """Extract column names from dataframe."""
        return tuple(self.displayed_df.columns.values.tolist())
    
    @on(DataTable.HeaderSelected)
    def sort_table(self, event : DataTable.HeaderSelected):
        column_name = self.displayed_df.columns[event.column_index]
        self.sort_ascending[column_name] = not self.sort_ascending.get(column_name, False)
        sort_order = self.sort_ascending[column_name]
        self.displayed_df = self.displayed_df.sort_values(by=column_name, ascending=sort_order)
        self.update_df(self.displayed_df)

    def filter_table(self, filters : DataFrameFilters):
        df = self.df[self.displayed_df.columns]
        nb_columns = len(df.columns)
        for filter in filters :
            if filter.column_index < nb_columns :
                column_name = self.displayed_df.columns[filter.column_index]
                if filter.exclude:
                    df = df[df.apply(lambda row: match_value(str(row[column_name]), filter.value), axis=1) == False]
                else:
                    df = df[df.apply(lambda row: match_value(str(row[column_name]), filter.value), axis=1) == True]
        self.update_df(df)

class FiltrableDataFrame(Static):
    DEFAULT_CSS = """
    FiltrableDataFrame {
        layout: grid;
        grid-size: 1 2;  /* 2 lines */
        grid-columns: 1fr;
        grid-rows: 8 1fr;
    }
    #table-option{
        row-span: 1;
    }
    #table-container{
        overflow-x: scroll;
        overflow-y: hidden;
        width: auto;
        height: 99%;
        row-span: 1;
    }

    #filter-container{
        width: auto;
        margin-top: 1;
        margin-bottom: 1;
        height: auto;
    }

    #selectmode{
        border-title-color: white;
    }

    DataFrameTable{
        height: auto;
        width: auto;
        overflow: hidden scroll;
    }

    #copy, #copy-table, #clean-filter {
        margin-top: 1
    }
    """

    columns_names = reactive([])

    def __init__(self, df, **kwargs):
        super().__init__(**kwargs)
        self.datatable = DataFrameTable(df)
        self.datatable.cursor_type = "cell"
        
        
    def on_mount(self):
        self.watch(self.datatable, "virtual_size", self.update_input_size, init=True)
        self.watch(self, "columns_names", self.update_columns_name, init=True)
        self.query_one("#columnselect").value = [(column, True) for column in self.datatable.df]

    def compose(self) -> ComposeResult:
        with Horizontal(id="table-option"):
            with RadioSet(id="selectmode") as radioset:
                    yield RadioButton("cell", value=True)
                    yield RadioButton("row")
                    yield RadioButton("column")
                    radioset.border_title = "Select :"
            yield Button("Copy selected",id="copy", variant="primary")
            yield Button("Copy table",id="copy-table", variant="primary")
            yield Button("Reset",id="clean-filter", variant="error")
            with Vertical() :
                yield Select([], prompt="Group by...", id="groupby")
                yield MultiSelect("", [], [], prompt="Columns to show...", id="columnselect")
        with ScrollableContainer(id="table-container"):
            yield Horizontal(*[FilterInput(id=f"filter-input-{i}") for i in range(len(self.datatable.displayed_df.columns)) ], id="filter-container")
            yield self.datatable
    
    def filter_columns(self):
        df = self.datatable.df
        filters = []
        for filter_input in self.query(FilterInput):
            input_field = filter_input.input
            reverse_search = filter_input.checkbox.value
            column_index = int(filter_input.id.split("-")[-1])
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
        pyperclip.copy(self.datatable.displayed_df.to_csv(sep="\t",index=False))

    @on(Button.Pressed, "#clean-filter")
    def clean_filters(self, reset_df = True):
        for input in self.query(FilterInput):
            input_field = input.query_one(Input)
            reverse_search = input.query_one(Checkbox)
            input_field.value = ''
            reverse_search.value = False
        if reset_df: 
            self.datatable.update_df(self.datatable.df)
        self.update_input_size()


    def update_input_size(self):
        nb_of_columns = len(self.datatable.columns.keys())
        self.columns_names = list(self.datatable.columns.keys())
        nb_of_inputs = len(self.query(FilterInput))
        # Update size of existing columns
        for column in self.datatable.columns.values() :
            input_index = str(self.datatable.get_column_index(column.key))
            if input := self.query(f"#filter-input-{input_index}"):
                input[0].styles.width = column.content_width + 2
                input[0].styles.hidden = False
            else:
                # Add inputs if needed
                self.query_one("#filter-container").mount(input := FilterInput(id=f"#filter-input-{input_index}"))
                input.styles.width = column.content_width + 2
                input.styles.hidden = False
        # Hide too many inputs
        if nb_of_inputs > nb_of_columns:
            for index in range(nb_of_columns,nb_of_inputs):
                input = self.query_one(f"#filter-input-{index}")
                input.styles.hidden = True
                input.styles.width = 0
    
    @on(MultiSelect.Changed)
    def update_displayed_columns(self, event : MultiSelect.Changed):
        if event.multi_select.id == "columnselect":
            columns_to_drop = set(self.datatable.df.columns) - set(event.multi_select.value)
            df = self.datatable.df
            clean_df = df.drop(columns=columns_to_drop, axis=1)
            self.datatable.update_df(clean_df)
            self.clean_filters(reset_df=False)

    @on(Select.Changed, "#groupby")
    def groupby_columns(self, event: Select.Changed):    
        df = self.datatable.df
        if event.value and event.value in df.columns:
            clean_df = df.groupby([f"{event.value}"], as_index=False).count()
            self.datatable.update_df(clean_df)
            self.clean_filters(reset_df=False)
        elif event.value == None:
            self.datatable.update_df(self.datatable.df)
            self.clean_filters()
        else:
            self.app.notify(f"Error while grouping by {event.value}",   severity="error")




    def update_columns_name(self):
        column_selector =  self.query_one("#columnselect")
        columns_options = [(column, True)  if column in column_selector.value else (column, False) for column in self.datatable.df.columns]
        column_selector.value = columns_options
        self.query_one("#groupby").set_options([(column, column) for column in self.datatable.df.columns])




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

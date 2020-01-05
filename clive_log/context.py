from . import fields
import os
import shutil

MOVE_UP_CODE = "\u001b[{n}A"
RETURN_CODE = "\r"
CLEAR_CODE = "\u001b[0J"  # clear from cursor until the end of the screen

# TODO this context approach doesn't make a lot of sense.  If we print to context1, then context2, then context3, weird things will happen
# How do we keep the write of a context between terminal writes from overwriting that text?

# TODO if we detect a terminal size change, ensure we appropriately delete the last n values

# TODO terminal width doesn't seem to work in multiplexers like tmux if resized during run

class Context:
    def __init__(self, name):
        self.name = name
        self.fields = []
        self.text_field_names = {}
        self.graph_field_names = {}
        self.cell_field_names = {}
        self.current_text = 0
        self.current_lines = 0

    # TODO the dictionary X_field_names approach is getting repetitive, streamline it, ordered dict maybe?
    def add_text_field(self, name):
        self.fields.append(fields.TextField(name))
        self.text_field_names[name] = len(self.fields) - 1

    def write_text_field(self, name, text):
        self.fields[self.text_field_names[name]].set_text(text)

    def add_graph_field(self, name, cfg=None):
        self.fields.append(fields.GraphField(name))
        self.graph_field_names[name] = len(self.fields) - 1

    def update_graph_field(self, name, series, cfg=None):
        self.fields[self.graph_field_names[name]].update_plot(series, cfg)

    def add_cell_field(self, name, num_cells):
        self.fields.append(fields.CellField(name, num_cells))
        self.cell_field_names[name] = len(self.fields) - 1
    
    def update_cell_field(self, name, cell, text):
        self.fields[self.cell_field_names[name]].set_text(cell, text)

    def display(self):
        self._write("\n")
        self._clear_current_text()
        current_width = self._get_terminal_width()
        for field in self.fields:
            text = field.get_display_text(current_width)
            self._write(text)
        self._write("\n")

    def _clear_current_text(self):
        # TODO we should probably execute a clear text command on each line
        print(MOVE_UP_CODE.format(n=self.current_lines), end="")
        print(CLEAR_CODE, end="")
        self.current_lines = 0

    def _get_terminal_width(self):
        #TODO this only works on linux, windows version?
        columns, rows = shutil.get_terminal_size(fallback=(80, 24))
        return columns

    def _write(self, text):
        newlines = text.count("\n")
        self.current_lines += newlines
        print(text, end="")
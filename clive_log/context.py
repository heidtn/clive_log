from . import fields
import os
import sys
import shutil
from collections import OrderedDict
import ctypes

# TODO move ANSI codes into a different folder
MOVE_UP_CODE = "\u001b[{n}A"
RETURN_CODE = "\r"
CLEAR_CODE = "\u001b[0J"  # clear from cursor until the end of the screen

# TODO this context approach doesn't make a lot of sense.  If we print to context1, then context2,
# then context1 again, weird things will happen. How do we keep the write of a context between
# terminal writes from overwriting that text? Should we even bother?

# TODO if we detect a terminal size change, ensure we appropriately delete the last n values

# TODO terminal width doesn't seem to work in multiplexers like tmux if resized during run

STD_OUTPUT_HANDLE = -11
ENABLE_PROCESSED_OUTPUT = 1
ENABLE_WRAP_AT_EOL_OUTPUT = 2
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 4
PRETTY_COLORS_IN_TERMINAL = ENABLE_VIRTUAL_TERMINAL_PROCESSING | \
                            ENABLE_WRAP_AT_EOL_OUTPUT | \
                            ENABLE_PROCESSED_OUTPUT


class Context:
    def __init__(self, name, autoset_windows=True):
        self.name = name
        self.fields = OrderedDict()
        self.text_field_names = OrderedDict()
        self.graph_field_names = OrderedDict()
        self.cell_field_names = OrderedDict()
        self.current_lines = 0
        if autoset_windows and os.name == 'nt':
            # This basically allows windows to use ANSI color codes. It will output
            # gibberish characters otherwise
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(STD_OUTPUT_HANDLE),
                                    PRETTY_COLORS_IN_TERMINAL)

    def add_text_field(self, name):
        """Create a new text field, will overwrite any existing one with the same name."""
        text_field = fields.TextField(name)
        self.fields[name] = text_field
        self.text_field_names[name] = text_field

    def write_text_field(self, name, text):
        """Sets the text field with a new string."""
        self.text_field_names[name].set_text(text)

    def add_graph_field(self, name, cfg=None):
        """Create a new graph field, will overwrite any existing one with the same name.
        Keyword arguments:
        name -- name of the graph field
        cfg -- dictionary to configure the graph.  Allowable settings are:
            'minimum' - minimum y value for the chart, autoscaled if not passed
            'maximum' - maximum y value for the chart, autoscaled if not passed
            'offset'  - offset spaces after y-axis label
            'height'  - height of the chart
            'format'  - format string for y-axis labels
        """
        graph_field = fields.GraphField(name)
        self.fields[name] = graph_field
        self.graph_field_names[name] = graph_field

    def update_graph_field(self, name, series, cfg=None):
        """Set the graph series.
        Keyword arguments:
        name -- name of the graph field
        series -- 1d list of values to graph
        cfg -- dictionary to configure the graph.  See add_graph_field for details.
        """ 
        self.graph_field_names[name].update_plot(series, cfg)

    def add_cell_field(self, name, num_cells):
        """Create a new cell field, will overwrite any existing one with the same name.
        Keyword arguments:
        name -- name of the cell field
        num_cells -- how many cells to create
        """
        cell_field = fields.CellField(name, num_cells)
        self.fields[name] = cell_field
        self.cell_field_names[name] = cell_field

    def update_cell_field(self, name, cell, text):
        """Update a single cell with text.
        Keyword arguments:
        name -- name of the cell field
        cell -- index of the cell
        text -- text to set the cell index
        """
        self.fields[name].set_text(cell, text)

    def display(self):
        """Write the current context to stdout."""
        # Insert a newline at the beginning so the current terminal line isn't overwritten
        self._write("\n")
        self._clear_current_text()
        current_width = self._get_terminal_width()
        for _, field in self.fields.items():
            text = field.get_display_text(current_width)
            self._write(text)

    def reset(self):
        """Calling this ensures a write to this context won't overwrite previously written text."""
        self.current_lines = 0

    def _clear_current_text(self):
        sys.stdout.write(MOVE_UP_CODE.format(n=self.current_lines))
        sys.stdout.write(CLEAR_CODE)
        self.current_lines = 0

    def _get_terminal_width(self):
        columns, _ = shutil.get_terminal_size(fallback=(80, 24))
        return columns

    def _write(self, text):
        newlines = text.count("\n")
        self.current_lines += newlines
        sys.stdout.write(text)

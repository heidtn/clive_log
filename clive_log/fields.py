from abc import ABC
import math

# TODO move ANSI codes into a different folder
# ANSI Color codes
RESET_COLOR_CODE = "\u001b[0m"
GREEN_COLOR_CODE = "\u001b[32m"
WHITE_COLOR_CODE = "\u001b[37m"


class Field(ABC):
    def get_display_text(self):
        raise NotImplementedError()


class TextField(Field):
    # TODO create a passable config for these symbols?
    HEADER_SYMBOL = "#"
    FOOTER_SYMBOL = "#"
    START_SYMBOL = "|"

    def __init__(self, name):
        self.name = name
        self.text = ""

    def set_text(self, text):
        self.text = str(text)

    def get_display_text(self, current_width):
        # TODO clean this up, minus 1 bad
        toshow = self.text[:current_width - len(self.START_SYMBOL) - 1]
        text = ""
        text += GREEN_COLOR_CODE + self.HEADER_SYMBOL*current_width + "\n"
        text += GREEN_COLOR_CODE + self.START_SYMBOL + WHITE_COLOR_CODE + " "
        text += toshow + "\n"
        text += GREEN_COLOR_CODE + self.HEADER_SYMBOL*current_width + "\n"
        text += RESET_COLOR_CODE
        return text


class CellField(Field):
    # TODO create a passable config for these symbols?
    HEADER_SYMBOL = "#"
    FOOTER_SYMBOL = "#"
    SEPARATOR_SYMBOL = "|"

    def __init__(self, name, num_cells):
        self.name = name
        self.num_cells = num_cells
        self.cells = ["" for i in range(num_cells)]

    def set_text(self, cell, text):
        self.cells[cell] = str(text)

    def get_display_text(self, current_width):
        text = ""
        text += GREEN_COLOR_CODE + self.HEADER_SYMBOL*current_width + "\n"
        text += self._generate_cell_text(current_width) + "\n"
        text += GREEN_COLOR_CODE + self.HEADER_SYMBOL*current_width + "\n"
        text += RESET_COLOR_CODE
        return text

    def _generate_cell_text(self, current_width):
        total_cell_text_width = current_width - self.num_cells - 1
        single_cell_text_width = total_cell_text_width // self.num_cells
        # Subtract one character to make room for the last separator
        last_cell_width = total_cell_text_width % self.num_cells + single_cell_text_width - 1
        separator_display = GREEN_COLOR_CODE + self.SEPARATOR_SYMBOL + RESET_COLOR_CODE
        text = ""
        for i in range(len(self.cells)):
            cell = self.cells[i]
            width = last_cell_width if i == len(self.cells) - 1 else single_cell_text_width
            cell_text = cell[:width]
            filler = " " * (width - len(cell_text))
            text += separator_display
            text += cell_text + filler
        text += separator_display

        return text


class GraphField(Field):
    # TODO allow multiple y plots
    # TODO is there a way to add x-axis labels without taking up a bunch of space?
    def __init__(self, name, cfg=None):
        self.name = name
        self.cfg = None
        self.series = None

    def update_plot(self, series, new_cfg=None):
        # TODO use *args here for multiple axes
        self.series = series
        if new_cfg:
            self.cfg = new_cfg

    def _simplify_series(self, series, max_size):
        # TODO perhaps allow averaging data here instead of aliasing data points?
        series_length = len(series)
        if series_length == max_size:
            return list(series)
        else:
            return self._create_simplified_series(series, series_length, max_size)

    def _create_simplified_series(self, series, series_length, max_size):
        simplified_series = []
        step_size = series_length / max_size
        for i in range(max_size):
            index = round(step_size * i)
            if index >= series_length:
                index = series_length - 1
            simplified_series.append(series[index])
        return simplified_series

    def get_display_text(self, current_width):
        # The following is ripped directly from:
        # https://github.com/kroitor/asciichart/blob/master/asciichartpy/__init__.py
        # thanks to Igor Kroitor for putting it together
        """ Possible cfg parameters are 'minimum', 'maximum', 'offset', 'height' and 'format'.
        cfg is a dictionary, thus dictionary syntax has to be used.
        Example: print(plot(series, { 'height' :10 }))
        """
        # TODO refactor this whole section for readability

        cfg = self.cfg or {}

        # TODO, bit of a catch-22 here.  Would rather get minimum and maximum from the
        # simplified series but that affects the ylabel text and thus the length of the
        # simplified series.  Is there a better way than using the full series?
        minimum = cfg['minimum'] if 'minimum' in cfg else min(self.series)
        maximum = cfg['maximum'] if 'maximum' in cfg else max(self.series)

        interval = abs(float(maximum) - float(minimum))
        offset = cfg['offset'] if 'offset' in cfg else 3
        height = cfg['height'] if 'height' in cfg else 12
        ratio = height / interval
        min2 = math.floor(float(minimum) * ratio)
        max2 = math.ceil(float(maximum) * ratio)

        intmin2 = int(min2)
        intmax2 = int(max2)

        rows = abs(intmax2 - intmin2)

        placeholder = cfg['format'] if 'format' in cfg else '{:8.2f} '
        actual_series_width = current_width - (len(placeholder) + offset)
        if actual_series_width <= 0:
            series = []
        else:
            series = self._simplify_series(self.series, actual_series_width)

        width = len(series) + offset

        result = [[' '] * width for i in range(rows + 1)]

        # axis and labels
        for y in range(intmin2, intmax2 + 1):
            label = placeholder.format(float(maximum) - ((y - intmin2) * interval / rows))
            result[y - intmin2][max(offset - len(label), 0)] = label
            result[y - intmin2][offset - 1] = '┼' if y == 0 else '┤'

        if actual_series_width <= 0:
            return '\n'.join([''.join(row) for row in result]) + '\n'

        y0 = int(series[0] * ratio - min2)
        result[rows - y0][offset - 1] = '┼'  # first value

        for x in range(0, len(series) - 1):  # plot the line
            y0 = int(round(series[x + 0] * ratio) - intmin2)
            y1 = int(round(series[x + 1] * ratio) - intmin2)
            if y0 == y1:
                result[rows - y0][x + offset] = '─'
            else:
                result[rows - y1][x + offset] = '╰' if y0 > y1 else '╭'
                result[rows - y0][x + offset] = '╮' if y0 > y1 else '╯'
                start = min(y0, y1) + 1
                end = max(y0, y1)
                for y in range(start, end):
                    result[rows - y][x + offset] = '│'

        return '\n'.join([''.join(row) for row in result]) + '\n'

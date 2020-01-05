import clive_log
import time
import numpy as np

context = clive_log.Context("test")
context.add_graph_field("test_graph")
context.add_text_field("text_field1")
context.add_text_field("text_field2")
CELL_COUNT = 12
context.add_cell_field("test_cells", CELL_COUNT)

words = "sphinx of black quartz judge my vow".split()
t = 0
while True:
    series = [7 * np.cos(i*0.25) for i in range(t, t+80)]
    word1 = words[t % len(words)]
    word2 = words[(t + 1) % len(words)]

    for i in range(CELL_COUNT):
        word = words[(i + t) % len(words)]
        context.update_cell_field("test_cells", i, word)

    context.update_graph_field("test_graph", series)
    context.write_text_field("text_field1", word1)
    context.write_text_field("text_field2", word2)
    context.display()

    t += 1
    time.sleep(0.1)


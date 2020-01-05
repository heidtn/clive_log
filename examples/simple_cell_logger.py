import clive_log
import time

words = "sphinx of black quartz judge my vow".split()
context = clive_log.Context("test")
CELL_COUNT = 4
context.add_cell_field("test_cells", CELL_COUNT)

index = 0
while True:
    for i in range(CELL_COUNT):
        word = words[(i + index) % len(words)]
        context.update_cell_field("test_cells", i, word)
    context.display()
    time.sleep(1.0)


import clive_log
import time
import numpy as np

context = clive_log.Context("test")
context.add_graph_field("test_graph")

t = 0
while True:
    series = [7 * np.cos(i*0.25) for i in range(t, t+100)]
    context.update_graph_field("test_graph", series)
    context.display()
    t += 1
    time.sleep(0.01)


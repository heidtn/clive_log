import clive_log
import time

words = "sphinx of black quartz judge my vow".split()
context = clive_log.Context("test")
context.add_text_field("field1")

index = 0
while True:
    word = words[index]
    index = (index + 1) % len(words)
    context.write_text_field("field1", word)
    context.display()
    #time.sleep(1.0)


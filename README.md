# CLIVE_LOG

This is a simple library for quick python debugging of live data streams.  It's intended to run in the command line only
and to be very compact.  The primary goals of the project are to not use any external dependencies (besides the python libraries)
and to try and keep the total LOC under ~1000 to make it accessible to new people.

### Getting started

Check the examples folder for some basic demos on how to use this library.

The general usage is:
```python
context = clive_log.Context("test")
context.add_text_field("text_field1")
while True:
    context.write_text_field("text_field1", "new text to write")
    context.display()
```

![clive_log Demo](clive_demo.gif)


### Known Issues

There are still some issues with the system, namely:
* artifacts when resizing
* nonfunctional in terminal multiplexers

### Future Features

Some things I would like to eventually add:
* config parameters for how to print everything
* resize cleanup
* progress bars
* tables

### License

MIT License
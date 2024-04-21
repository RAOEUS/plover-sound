# Plover Sound

This is my first iteration! Right now, it just plays a sine wave melody or a keyboard click sound with each stroke.

To use the sine melody set the `use_sample` parameter to `True` and reinstall (and vice versa to go back to the keyboard click)
```python
def on_stroked(self, stroke, use_sample=False):
# Change use_sample to True
def on_stroked(self, stroke, use_sample=True):
```

## Installation

You have to install manually from the command line.

See the instructions [here](https://plover.wiki/index.php/Plugins).

For Windows:

```
.\plover_console.exe -s plover_plugins install git+https://github.com/RAOEUS/plover-sounds.git

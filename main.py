import os
import src.interface

# For monitors with low resolution / high dpi scaling, reduce scale
scale = 1.0

app = src.interface.Interface(scale)
app.launch()

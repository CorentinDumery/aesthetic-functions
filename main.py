

import os
import src.interface

size = (960, 540)
if os.name == 'nt':  # smaller size for Windows
    size = (640, 360)

app = src.interface.Interface(size)
app.launch()

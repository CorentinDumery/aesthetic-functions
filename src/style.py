import tkinter as tk

main_color = "#f1faee"
secondary_color = "#e1eade"

# Convention:
# "_style" is used when creating tk widget
# "_grid" is used when doing widget.grid(...)


base_style = {
    'bg': secondary_color,
    'highlightthickness': 0
}

frame_style = {
    **base_style,
    'padx': 5,
    'pady': 5,
    'bd': 10,
    'relief': tk.RIDGE
}

frame_grid = {
    'sticky': tk.E+tk.W+tk.N+tk.S
}

button_grid = {
    'sticky': tk.E+tk.W+tk.N+tk.S
}

title_style = {
    **base_style,
    'font': ("Courier", 18, "bold"),
    'justify': 'center'
}

scale_style = {
    **base_style,
    'from_': 0,
    'to_': 255,
    'length': 150
}

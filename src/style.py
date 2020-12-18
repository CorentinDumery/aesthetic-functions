import tkinter as tk

mainColor = "#f1faee"
secondaryColor = "#e1eade"

#Convention: 
# "Style" is used when creating tk widget
# "Grid" is used when doing widget.grid(...)


baseStyle = {
    'bg': secondaryColor,
    'highlightthickness': 0
}

frameStyle = {
    **baseStyle,
    'padx': 5,
    'pady': 5,
    'bd': 10,
    'relief': tk.RIDGE
}

frameGrid = {
    'sticky': tk.E+tk.W+tk.N+tk.S
}

titleStyle = {
    **baseStyle,
    'font': ("Courier", 18, "bold"),
    'justify': 'center'
}

scaleStyle = {
    **baseStyle
}

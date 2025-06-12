import tkinter as tk

def create_alarm_placeholder(parent, color='gray', diameter=20):
    """
    Create a circular alarm placeholder as a Canvas widget.
    Args:
        parent: The parent tkinter widget.
        color: Fill color of the circle.
        diameter: Diameter of the circle in pixels.
    Returns:
        The Canvas widget containing the circle.
    """
    canvas = tk.Canvas(parent, width=diameter, height=diameter, highlightthickness=0, bg=parent.cget('bg'))
    canvas.create_oval(2, 2, diameter-2, diameter-2, fill=color, outline='black')
    return canvas

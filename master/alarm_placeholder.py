import tkinter as tk

def create_alarm_placeholder(parent, color='gray', diameter=20):
    """
    Create a circular alarm placeholder as a Canvas widget.
    Args:
        parent: The parent tkinter widget.
        color: Fill color of the circle.
        diameter: Diameter of the circle in pixels.
    Returns:
        The Canvas widget containing the circle and a method to control blinking.
    """
    canvas = tk.Canvas(parent, width=diameter, height=diameter, highlightthickness=0, bg=parent.cget('bg'))
    oval = canvas.create_oval(2, 2, diameter-2, diameter-2, fill=color, outline='black')
    canvas._blinking = False
    canvas._blink_job = None
    canvas._acknowledged = False
    canvas._json_alarm_state = 0 if color == 'gray' else 1

    def start_blinking():
        if canvas._blinking:
            return
        canvas._blinking = True
        canvas._acknowledged = False
        def blink():
            if not canvas._blinking or canvas._acknowledged:
                canvas.itemconfig(oval, fill='gray')
                canvas._json_alarm_state = 0
                if hasattr(canvas.master, 'event_generate'):
                    canvas.master.event_generate('<<AlarmBlink>>', when='tail')
                return
            current_color = canvas.itemcget(oval, 'fill')
            new_color = 'red' if current_color == 'gray' else 'gray'
            canvas.itemconfig(oval, fill=new_color)
            canvas._json_alarm_state = 1 if new_color == 'red' else 0
            if hasattr(canvas.master, 'event_generate'):
                canvas.master.event_generate('<<AlarmBlink>>', when='tail')
            canvas._blink_job = canvas.after(400, blink)
        blink()

    def stop_blinking():
        canvas._blinking = False
        canvas._acknowledged = True
        if canvas._blink_job:
            canvas.after_cancel(canvas._blink_job)
            canvas._blink_job = None
        canvas.itemconfig(oval, fill='gray')
        canvas._json_alarm_state = 0
        if hasattr(canvas.master, 'event_generate'):
            canvas.master.event_generate('<<AlarmBlink>>', when='tail')

    canvas.start_blinking = start_blinking
    canvas.stop_blinking = stop_blinking
    return canvas

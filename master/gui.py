import tkinter as tk
from tkinter import messagebox, scrolledtext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HMIWidgets:
    def __init__(self, master, devices, send_command_cb, broadcast_cb, check_user_access_cb, show_user_ids_cb, set_pwm_cb=None):
        self.master = master
        self.devices = devices
        self.send_command_cb = send_command_cb
        self.broadcast_cb = broadcast_cb
        self.check_user_access_cb = check_user_access_cb
        self.show_user_ids_cb = show_user_ids_cb
        self.set_pwm_cb = set_pwm_cb
        self.widgets = {}

    def build_layout(self):
        # Main layout: left (controls), right (trend), bottom (logs)
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill='both', expand=True)
        self.widgets['main_frame'] = main_frame

        # Left panel: Device controls
        left_panel = tk.LabelFrame(main_frame, text="Device Controls", font=("Arial", 10, "bold"), padx=8, pady=8)
        left_panel.grid(row=0, column=0, sticky='nsw', padx=8, pady=8)
        lock_frame = tk.LabelFrame(left_panel, text="Locks", font=("Arial", 9, "bold"), padx=4, pady=4)
        lock_frame.pack(fill='x', pady=(0,8))
        light_frame = tk.LabelFrame(left_panel, text="Lights", font=("Arial", 9, "bold"), padx=4, pady=4)
        light_frame.pack(fill='x')
        for name, info in self.devices.items():
            if info['type'] == 'lock':
                frame = tk.Frame(lock_frame)
                frame.pack(fill='x', pady=2)
                tk.Label(frame, text=name, width=10, anchor='w').pack(side='left')
                tk.Button(frame, text='LOCK', width=7, command=lambda n=name: self.send_command_cb(n, 'LOCK')).pack(side='left', padx=2)
                tk.Button(frame, text='UNLOCK', width=7, command=lambda n=name: self.send_command_cb(n, 'UNLOCK')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST LOCK', width=14, command=lambda n=name: self.broadcast_cb(n, 'LOCK')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST UNLOCK', width=14, command=lambda n=name: self.broadcast_cb(n, 'UNLOCK')).pack(side='left', padx=2)
            elif info['type'] == 'light':
                frame = tk.Frame(light_frame)
                frame.pack(fill='x', pady=2)
                tk.Label(frame, text=name, width=10, anchor='w').pack(side='left')
                tk.Button(frame, text='ON', width=7, command=lambda n=name: self.send_command_cb(n, 'ON')).pack(side='left', padx=2)
                tk.Button(frame, text='OFF', width=7, command=lambda n=name: self.send_command_cb(n, 'OFF')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST ON', width=12, command=lambda n=name: self.broadcast_cb(n, 'ON')).pack(side='left', padx=2)
                tk.Button(frame, text='BROADCAST OFF', width=12, command=lambda n=name: self.broadcast_cb(n, 'OFF')).pack(side='left', padx=2)
                # PWM slider and AUTO/MANUAL toggle
                if self.set_pwm_cb:
                    pwm_mode = {'mode': 'auto'}  # mutable holder for mode
                    def toggle_pwm_mode(slider, toggle_btn, device_name):
                        if pwm_mode['mode'] == 'auto':
                            pwm_mode['mode'] = 'manual'
                            slider.config(state='normal')
                            toggle_btn.config(text='MANUAL')
                            self.send_command_cb(device_name, 'PWM_MANUAL')
                        else:
                            pwm_mode['mode'] = 'auto'
                            slider.config(state='disabled')
                            toggle_btn.config(text='AUTO')
                            self.send_command_cb(device_name, 'PWM_AUTO')
                    pwm_slider = tk.Scale(frame, from_=0, to=1023, orient='horizontal', length=120, label='PWM',
                                         command=lambda val, n=name: self.set_pwm_cb(n, int(val)))
                    pwm_slider.set(128)
                    pwm_slider.config(state='disabled')
                    pwm_slider.pack(side='left', padx=4)
                    toggle_btn = tk.Button(frame, text='AUTO', width=7)
                    toggle_btn.pack(side='left', padx=2)
                    toggle_btn.config(command=lambda s=pwm_slider, b=toggle_btn, n=name: toggle_pwm_mode(s, b, n))
                    self.widgets[f'{name}_pwm_slider'] = pwm_slider
                    self.widgets[f'{name}_pwm_toggle_btn'] = toggle_btn
        self.widgets['lock_frame'] = lock_frame
        self.widgets['light_frame'] = light_frame

        # Right panel: Trend chart
        right_panel = tk.LabelFrame(main_frame, text="Trend Visualization", font=("Arial", 10, "bold"), padx=8, pady=8)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=8, pady=8)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        tk.Label(right_panel, text="Lux Trend", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=(5,0))
        lux_fig = Figure(figsize=(3.5, 1.5), dpi=90)
        lux_ax = lux_fig.add_subplot(111)
        lux_ax.set_ylim(0, 12)
        lux_ax.set_yticks([i for i in range(0, 13)])
        lux_ax.set_ylabel('Lux')
        lux_ax.set_xlabel('Time')
        lux_canvas = FigureCanvasTkAgg(lux_fig, master=right_panel)
        lux_canvas_widget = lux_canvas.get_tk_widget()
        lux_canvas_widget.pack(padx=5, pady=5, fill='both', expand=True)
        self.widgets['lux_fig'] = lux_fig
        self.widgets['lux_ax'] = lux_ax
        self.widgets['lux_canvas'] = lux_canvas
        self.widgets['lux_canvas_widget'] = lux_canvas_widget

        # Bottom panel: Logs
        bottom_panel = tk.LabelFrame(self.master, text="Logs", font=("Arial", 10, "bold"), padx=8, pady=8)
        bottom_panel.pack(fill='x', padx=8, pady=(0,8), side='bottom')
        log_frame = tk.Frame(bottom_panel)
        log_frame.pack(fill='x')
        # Outgoing log
        out_frame = tk.Frame(log_frame)
        out_frame.pack(side='left', fill='both', expand=True, padx=(0,8))
        tk.Label(out_frame, text='Outgoing Log', font=("Arial", 9, "bold")).pack(anchor='w')
        log_area = scrolledtext.ScrolledText(out_frame, width=40, height=7, state='disabled')
        log_area.pack(fill='both', expand=True)
        # Incoming log
        in_frame = tk.Frame(log_frame)
        in_frame.pack(side='left', fill='both', expand=True)
        tk.Label(in_frame, text='Incoming Log', font=("Arial", 9, "bold")).pack(anchor='w')
        incoming_log_area = scrolledtext.ScrolledText(in_frame, width=40, height=7, state='disabled')
        incoming_log_area.pack(fill='both', expand=True)
        self.widgets['log_area'] = log_area
        self.widgets['incoming_log_area'] = incoming_log_area

        # Add SQL DB controls
        db_frame = tk.LabelFrame(self.master, text="SQL DB Tools", font=("Arial", 10, "bold"), padx=8, pady=8)
        db_frame.pack(fill='x', padx=8, pady=(0,8), side='bottom')
        tk.Button(db_frame, text='Show All User IDs', command=self.show_user_ids_cb).pack(side='left', padx=4)
        tk.Label(db_frame, text='Check Access for User ID:').pack(side='left', padx=4)
        user_id_entry = tk.Entry(db_frame, width=12)
        user_id_entry.pack(side='left', padx=2)
        tk.Label(db_frame, text='IP:').pack(side='left', padx=2)
        ip_entry = tk.Entry(db_frame, width=15)
        ip_entry.pack(side='left', padx=2)
        tk.Button(db_frame, text='Check Access', command=lambda: self.check_user_access_cb(user_id_entry.get(), ip_entry.get())).pack(side='left', padx=4)
        self.widgets['user_id_entry'] = user_id_entry
        self.widgets['ip_entry'] = ip_entry

        return self.widgets

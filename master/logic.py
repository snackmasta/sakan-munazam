class LuxTrendLogic:
    def __init__(self, max_lux_points=75):
        self.lux_data = []
        self.max_lux_points = max_lux_points

    def update_lux_from_msg(self, msg, draw_callback):
        try:
            color = 'blue'  # default
            dev = None
            if 'light_207' in msg:
                color = 'red'
                dev = 'light_207'
            elif 'light_208' in msg:
                color = 'blue'
                dev = 'light_208'
            if 'light_' in msg:
                parts = msg.split(':')
                for part in parts:
                    part = part.strip()
                    if '.' in part:
                        try:
                            lux = float(part)
                            self.lux_data.append((lux, color, dev))
                            if len(self.lux_data) > self.max_lux_points:
                                self.lux_data = self.lux_data[-self.max_lux_points:]
                            draw_callback()
                            break
                        except ValueError:
                            continue
        except Exception:
            pass

    def draw_lux_trend(self, ax, canvas):
        ax.clear()
        if not self.lux_data:
            ax.set_ylim(0, 75)
            ax.set_yticks([i for i in range(0, 76, 5)])
            ax.set_ylabel('Lux')
            ax.set_xlabel('Sample')
            ax.grid(True, linestyle='--', alpha=0.5)
            canvas.draw()
            return
        data_207 = [(i, lux) for i, (lux, color, dev) in enumerate([(v[0], v[1], v[2] if len(v) > 2 else None) for v in self.lux_data]) if dev == 'light_207']
        data_208 = [(i, lux) for i, (lux, color, dev) in enumerate([(v[0], v[1], v[2] if len(v) > 2 else None) for v in self.lux_data]) if dev == 'light_208']
        if data_207:
            x_207, y_207 = zip(*data_207)
            ax.plot(x_207, y_207, color='red', label='light_207')
        if data_208:
            x_208, y_208 = zip(*data_208)
            ax.plot(x_208, y_208, color='blue', label='light_208')
        ax.set_ylim(0, 75)
        ax.set_yticks([i for i in range(0, 76, 5)])
        ax.set_ylabel('Lux')
        ax.set_xlabel('Sample')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.figure.tight_layout()
        canvas.draw()

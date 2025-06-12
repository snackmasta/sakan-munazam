import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
from opcua import Client, ua
import threading

OPC_ENDPOINT = "opc.tcp://192.168.100.115:49320"
TAG_NODEID = "ns=2;s=ROOM 207.Device1.SliderValue"

class SliderOPCClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OPC UA Slider Control")
        self.setGeometry(100, 100, 400, 150)
        layout = QVBoxLayout()

        self.label = QLabel("Slider Value: 0.0", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1023)
        self.slider.setValue(0)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.on_slider_change)
        layout.addWidget(self.slider)

        self.setLayout(layout)

        self.client = Client(OPC_ENDPOINT)
        self.opc_thread = threading.Thread(target=self.opc_connect, daemon=True)
        self.opc_thread.start()

    def opc_connect(self):
        try:
            self.client.connect()
            node = self.client.get_node(TAG_NODEID)
            # Read initial value
            val = node.get_value()
            self.slider.setValue(int(val))
            self.label.setText(f"Slider Value: {val}")
            self.node = node
        except Exception as e:
            self.label.setText(f"OPC Error: {e}")
            self.node = None

    def on_slider_change(self, value):
        self.label.setText(f"Slider Value: {value}")
        # Write to OPC tag in a thread to avoid UI freeze
        threading.Thread(target=self.write_value, args=(value,), daemon=True).start()

    def write_value(self, value):
        try:
            if hasattr(self, 'node') and self.node is not None:
                # Get the current data type of the node
                variant_type = self.node.get_data_type_as_variant_type()
                # Convert value to the correct type
                if variant_type.name == 'Double':
                    v = float(value)
                elif variant_type.name in ['Int16', 'Int32', 'Int64', 'UInt16', 'UInt32', 'UInt64', 'Byte', 'SByte']:
                    v = int(value)
                else:
                    v = value
                self.node.set_value(ua.DataValue(ua.Variant(v, variant_type)))
        except Exception as e:
            self.label.setText(f"Write Error: {e}")

    def closeEvent(self, event):
        try:
            self.client.disconnect()
        except Exception:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SliderOPCClient()
    window.show()
    sys.exit(app.exec_())

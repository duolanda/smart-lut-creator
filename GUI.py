import os
import PySide6

dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

'''
上面的部分用来解决如下报错： 
qt.qpa.plugin: Could not find the Qt platform plugin "windows" in ""
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
'''

from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow

class LutUI():
    def __init__(self):
        self.window = QMainWindow()
        self.window.resize(800, 600)
        self.window.setWindowTitle("Smart LUT Creator")

        self.layout = QVBoxLayout()
        self.layout.addWidget(QPushButton('Top'))
        self.layout.addWidget(QPushButton('Bottom'))
        self.window.setLayout(self.layout)


app = QApplication([])
app.setStyle('Fusion')
lut_ui = LutUI()
lut_ui.window.show()
app.exec_()
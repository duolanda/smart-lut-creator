from PySide6.QtCore import Signal, QObject


class my_signal(QObject):
    drop_img = Signal(str)


mysgn = my_signal()

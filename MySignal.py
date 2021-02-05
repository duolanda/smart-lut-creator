from PySide6.QtCore import Signal, QObject


class MySignal(QObject):
    drop_img = Signal(str)


mysgn = MySignal()

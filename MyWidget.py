from PySide6.QtWidgets import QGraphicsView
from MySignal import mysgn

class myQGraphicsView(QGraphicsView):
    #这个文件主要是为了可以拖动打开图片
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        file_path = event.mimeData().text()
        if file_path.endswith('.jpg') or file_path.endswith('.png') or file_path.endswith('.tif') or file_path.endswith('.bmp'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event): 
        path = event.mimeData().text().replace('file:///', '') # 删除多余开头
        mysgn.drop_img.emit(path)



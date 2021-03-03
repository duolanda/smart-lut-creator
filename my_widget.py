from PySide6.QtWidgets import QGraphicsView
from my_signal import mysgn

class myQGraphicsView(QGraphicsView):
    #这个文件主要是为了可以拖动打开图片
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        #这段其实放到 GUI.py 的 eventFilter 里效果也是一样的
        file_path = event.mimeData().text()
        if file_path.endswith('.jpg') or file_path.endswith('.png') or file_path.endswith('.tif') or file_path.endswith('.tiff') or file_path.endswith('.bmp'):
            event.accept()
        else:
            event.ignore()

    # def dropEvent(self, event): 
    #     path = event.mimeData().text().replace('file:///', '') # 删除多余开头
    #     mysgn.drop_img.emit(path)




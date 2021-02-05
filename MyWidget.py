from PySide6.QtWidgets import QGraphicsView

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
        self.open_img(path)

    def open_img(self, file_name):
        '''
        输入图像
        '''
        global img
        img = colour.read_image(file_name)
        img = (img*255).astype(np.uint8)
        self.zoomscale=1                                                      

        frame = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix) #创建像素图元
        self.scene = QGraphicsScene() #创建场景
        self.scene.addItem(self.item)
        self.ui.graphicsView.setScene(self.scene) #将场景添加至视图

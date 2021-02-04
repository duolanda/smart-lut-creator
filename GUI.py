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

from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QImage, QPixmap

import colour
import numpy as np

class LutUI():
    def __init__(self):
        qfile_gui = QFile("Smart LUT Creator.ui")
        qfile_gui.open(QFile.ReadOnly)
        qfile_gui.close()

        self.ui = QUiLoader().load(qfile_gui)

        self.ui.keyPressEvent = self.keyPressEvent
        self.ui.openImage.triggered.connect(self.open_img)


    def open_img(self):
        '''
        打开图像
        '''
        openfile_name = QFileDialog.getOpenFileNames(self.ui, '选择文件', '.', "Image Files(*.jpg *.png *.tif *.bmp)") #.代表是当前目录

        file_name = openfile_name[0][0]

        img = colour.read_image(file_name)
        img = (img*255).astype(np.uint8)
        self.zoomscale=1                                                      

        frame = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix) #创建像素图元
        self.scene = QGraphicsScene() #创建场景
        self.scene.addItem(self.item)
        self.ui.graphicsView.setScene(self.scene) #将场景添加至视图

    def zoomin(self):
        """
        缩小图像
        """
        self.zoomscale=self.zoomscale-0.05
        if self.zoomscale<=0:
           self.zoomscale=0.2
        self.item.setScale(self.zoomscale)                               
 
    
    def zoomout(self):
        """
        点击方法图像
        """
        self.zoomscale=self.zoomscale+0.05
        if self.zoomscale>=5:
            self.zoomscale=5
        self.item.setScale(self.zoomscale) 

    def keyPressEvent(self, event):
        print("按下：" + str(event.key()))
        if event.key() == Qt.Key.Key_Equal: # =
            # self.zoomout()
            print('=')
        if event.key() == Qt.Key.Key_hyphen: # -
            # self.zoomin()
            print('-')


app = QApplication([])
app.setStyle('WindowsVista')
lut_ui = LutUI()
lut_ui.ui.show()
app.exec_()
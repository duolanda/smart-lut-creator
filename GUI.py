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
from MyWidget import  myQGraphicsView
from MySignal import mysgn


import colour
import numpy as np
from lut_color_enhance import rgb_color_enhance

class LutUI():
    def __init__(self):
        qfile_gui = QFile("Smart LUT Creator.ui")
        qfile_gui.open(QFile.ReadOnly)
        qfile_gui.close()

        loader = QUiLoader()
        loader.registerCustomWidget(myQGraphicsView)
        self.ui = loader.load(qfile_gui)

        self.sgn = mysgn
        self.sgn.drop_img.connect(self.open_img)

        self.init_color_enhence()

        self.ui.openImage.triggered.connect(self.img_window)
        self.ui.zoomInButton.clicked.connect(self.zoomin)
        self.ui.zoomOutButton.clicked.connect(self.zoomout)

        self.ui.brightnessSlider.valueChanged.connect(lambda: self.brightness_edit()) #用lambda传参
        self.ui.contrastSlider.valueChanged.connect(lambda: self.contrast_edit())
        self.ui.exposureSlider.valueChanged.connect(lambda: self.exposure_edit())
        self.ui.saturationSlider.valueChanged.connect(lambda: self.saturation_edit())
        self.ui.vibranceSlider.valueChanged.connect(lambda: self.vibrance_edit())
        self.ui.warmthSlider.valueChanged.connect(lambda: self.warmth_edit())

        self.ui.brightnessLineEdit.textChanged.connect(lambda: self.brightness_edit(True))
        self.ui.contrastLineEdit.textChanged.connect(lambda: self.contrast_edit(True))
        self.ui.exposureLineEdit.textChanged.connect(lambda: self.exposure_edit(True))
        self.ui.saturationLineEdit.textChanged.connect(lambda: self.saturation_edit(True))
        self.ui.vibranceLineEdit.textChanged.connect(lambda: self.vibrance_edit(True))
        self.ui.warmthLineEdit.textChanged.connect(lambda: self.warmth_edit(True))

        

    def init_color_enhence(self):
        # 滑块只支持 int，所以要做个映射，滑块-100~100 对应文本框 -1~1
        brightnessSlider = self.ui.brightnessSlider
        contrastSlider = self.ui.contrastSlider
        exposureSlider = self.ui.exposureSlider
        saturationSlider = self.ui.saturationSlider
        vibranceSlider = self.ui.vibranceSlider
        warmthSlider = self.ui.warmthSlider

        brightnessSlider.setMinimum(-100)	
        brightnessSlider.setMaximum(100)	

        contrastSlider.setMinimum(-100)	
        contrastSlider.setMaximum(500)	

        exposureSlider.setMinimum(-500)	
        exposureSlider.setMaximum(500)	

        saturationSlider.setMinimum(-100)	
        saturationSlider.setMaximum(500)	

        vibranceSlider.setMinimum(-100)	
        vibranceSlider.setMaximum(500)	

        warmthSlider.setMinimum(-100)	
        warmthSlider.setMaximum(100)	

        self.ui.brightnessLineEdit.setText(str(brightnessSlider.value()))
        self.ui.contrastLineEdit.setText(str(contrastSlider.value()))
        self.ui.exposureLineEdit.setText(str(exposureSlider.value()))
        self.ui.saturationLineEdit.setText(str(saturationSlider.value()))
        self.ui.vibranceLineEdit.setText(str(vibranceSlider.value()))
        self.ui.warmthLineEdit.setText(str(warmthSlider.value()))

    def img_window(self):
        '''
        打开图像选择窗口
        '''
        openfile_name = QFileDialog.getOpenFileNames(self.ui, '选择文件', '.', "Image Files(*.jpg *.png *.tif *.bmp)") #.代表是当前目录

        file_name = openfile_name[0][0]
        self.open_img(file_name)

        

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
        # self.ui.graphicsView = myQGraphicsView()
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
        放大图像
        """
        self.zoomscale=self.zoomscale+0.05
        if self.zoomscale>=5:
            self.zoomscale=5
        self.item.setScale(self.zoomscale) 

    def brightness_edit(self, line= False):
        '''
        调整亮度
        '''
        # 真正用的时候应该是对 lut 而不是图像操作，这个 lut 应该是一个 numpy 数组或自己定义的对象

        if line: #如果是修改了edit line
            self.ui.brightnessSlider.setValue(int(float(self.ui.brightnessLineEdit.text())*100))

        global img
        value = self.ui.brightnessSlider.value()/100
        self.ui.brightnessLineEdit.setText(str(value))
        img_out = (img/255).astype(np.float32)
        img_out = rgb_color_enhance(img_out, brightness = value)
        self.update_img(img_out)

    def contrast_edit(self, line= False):
        '''
        调整对比度
        '''
        if line: 
            self.ui.contrastSlider.setValue(int(float(self.ui.contrastLineEdit.text())*100))

        global img
        value = self.ui.contrastSlider.value()/100
        self.ui.contrastLineEdit.setText(str(value))
        img_out = (img/255).astype(np.float32)
        img_out = rgb_color_enhance(img_out, contrast = value)
        self.update_img(img_out)
        
    def exposure_edit(self, line= False):
        '''
        调整曝光
        '''
        if line: 
            self.ui.exposureSlider.setValue(int(float(self.ui.exposureLineEdit.text())*100))

        global img
        value = self.ui.exposureSlider.value()/100
        self.ui.exposureLineEdit.setText(str(value))
        img_out = (img/255).astype(np.float32)
        img_out = rgb_color_enhance(img_out, exposure = value)
        self.update_img(img_out)

    def saturation_edit(self, line= False):
        '''
        调整饱和度
        '''
        if line: 
            self.ui.saturationSlider.setValue(int(float(self.ui.saturationLineEdit.text())*100))

        global img
        value = self.ui.saturationSlider.value()/100
        self.ui.saturationLineEdit.setText(str(value))
        img_out = (img/255).astype(np.float32)
        img_out = rgb_color_enhance(img_out, saturation = value)
        self.update_img(img_out)

    def vibrance_edit(self, line= False):
        '''
        调整自然饱和度
        '''
        if line: 
            self.ui.vibranceSlider.setValue(int(float(self.ui.vibranceLineEdit.text())*100))

        global img
        value = self.ui.vibranceSlider.value()/100
        self.ui.vibranceLineEdit.setText(str(value))
        img_out = (img/255).astype(np.float32)
        img_out = rgb_color_enhance(img_out, vibrance = value)
        self.update_img(img_out)

    def warmth_edit(self, line= False):
        '''
        调整色温
        '''
        if line: 
            self.ui.warmthSlider.setValue(int(float(self.ui.warmthLineEdit.text())*100))

        global img
        value = self.ui.warmthSlider.value()/100
        self.ui.warmthLineEdit.setText(str(value))
        img_out = (img/255).astype(np.float32)
        img_out = rgb_color_enhance(img_out, warmth = value)
        self.update_img(img_out)

    def update_img(self, img_out):
        '''
        将处理后的图片显示到 UI 上
        '''
        img_out = (img_out*255).astype(np.uint8)
        frame = QImage(img_out, img_out.shape[1], img_out.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item.setPixmap(pix) 


app = QApplication([])
app.setStyle('WindowsVista')
lut_ui = LutUI()
lut_ui.ui.show()
app.exec_()
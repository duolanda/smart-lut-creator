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
import time
from lut_color_enhance import rgb_color_enhance
from lut_color_space import gamma_convert, gamut_convert
from lut_compute import compute_lut_np
from lut_preview import apply_lut_np


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

        self.ui.openImage.triggered.connect(self.img_window)
        self.ui.zoomInButton.clicked.connect(self.zoomin)
        self.ui.zoomOutButton.clicked.connect(self.zoomout)

        #色彩空间转换
        gamut_list = ['sRGB', 'Sony S-Gamut/S-Gamut3', 'Arri Wide Gamut']
        gamma_list = ['Linear', 'sRGB', 'Rec.709', 'Sony S-Log3', 'Arri LogC EI 800']
        wp_list = ['D65', 'A', 'C', 'D50', 'D55', 'D75']
        self.ui.inGamut.addItems(gamut_list)
        self.ui.inGamma.addItems(gamma_list)
        self.ui.inWp.addItems(wp_list)
        self.ui.outGamut.addItems(gamut_list)
        self.ui.outGamma.addItems(gamma_list)
        self.ui.outWp.addItems(wp_list)

        # self.ui.inGamut.currentIndexChanged.connect(convert_gamut)
        # self.ui.outGamut.currentIndexChanged.connect(convert_gamut)

        # self.ui.inGamma.currentIndexChanged.connect(convert_gamma)
        # self.ui.outGamma.currentIndexChanged.connect(convert_gamma)

        # self.ui.inWp.currentIndexChanged.connect(convert_wp)
        # self.ui.outWp.currentIndexChanged.connect(convert_wp)

        self.ui.inGamut.currentIndexChanged.connect(self.convert_cs)
        self.ui.outGamut.currentIndexChanged.connect(self.convert_cs)

        self.ui.inGamma.currentIndexChanged.connect(self.convert_cs)
        self.ui.outGamma.currentIndexChanged.connect(self.convert_cs)

        self.ui.inWp.currentIndexChanged.connect(self.convert_cs)
        self.ui.outWp.currentIndexChanged.connect(self.convert_cs)


        # 一级校色滑块
        self.init_color_enhence()

        self.ui.brightnessSlider.valueChanged.connect(lambda: self.brightness_edit()) #用lambda传参
        self.ui.contrastSlider.valueChanged.connect(lambda: self.contrast_edit())
        self.ui.exposureSlider.valueChanged.connect(lambda: self.exposure_edit())
        self.ui.saturationSlider.valueChanged.connect(lambda: self.saturation_edit())
        self.ui.vibranceSlider.valueChanged.connect(lambda: self.vibrance_edit())
        self.ui.warmthSlider.valueChanged.connect(lambda: self.warmth_edit())
        self.ui.tintSlider.valueChanged.connect(lambda: self.tint_edit())


        self.ui.brightnessLineEdit.textChanged.connect(lambda: self.brightness_edit(True))
        self.ui.contrastLineEdit.textChanged.connect(lambda: self.contrast_edit(True))
        self.ui.exposureLineEdit.textChanged.connect(lambda: self.exposure_edit(True))
        self.ui.saturationLineEdit.textChanged.connect(lambda: self.saturation_edit(True))
        self.ui.vibranceLineEdit.textChanged.connect(lambda: self.vibrance_edit(True))
        self.ui.warmthLineEdit.textChanged.connect(lambda: self.warmth_edit(True))
        self.ui.tintLineEdit.textChanged.connect(lambda: self.tint_edit(True))


        self.hald_img = colour.read_image('HALD_36.png')
        self.open_img('test_img/panel.jpg', reset = False)  #默认测试图片





        

    def init_color_enhence(self):
        # 滑块只支持 int，所以要做个映射，滑块-100~100 对应文本框 -1~1
        global enhence_list
        enhence_list = [0,0,0,0,0,0,0] #亮度、对比度、曝光、饱和度、自然饱和度、色温、色调

        brightnessSlider = self.ui.brightnessSlider
        contrastSlider = self.ui.contrastSlider
        exposureSlider = self.ui.exposureSlider
        saturationSlider = self.ui.saturationSlider
        vibranceSlider = self.ui.vibranceSlider
        warmthSlider = self.ui.warmthSlider
        tintSlider = self.ui.tintSlider


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

        tintSlider.setMinimum(-50)	
        tintSlider.setMaximum(50)	

        self.ui.brightnessLineEdit.setText(str(brightnessSlider.value()))
        self.ui.contrastLineEdit.setText(str(contrastSlider.value()))
        self.ui.exposureLineEdit.setText(str(exposureSlider.value()))
        self.ui.saturationLineEdit.setText(str(saturationSlider.value()))
        self.ui.vibranceLineEdit.setText(str(vibranceSlider.value()))
        self.ui.warmthLineEdit.setText(str(warmthSlider.value()))
        self.ui.tintLineEdit.setText(str(tintSlider.value()))

    def img_window(self):
        '''
        打开图像选择窗口
        '''
        openfile_name = QFileDialog.getOpenFileNames(self.ui, '选择文件', '.', "Image Files(*.jpg *.png *.tif *.bmp)") #.代表是当前目录

        file_name = openfile_name[0][0]
        self.open_img(file_name)

        

    def open_img(self, file_name, reset = True):
        '''
        输入图像
        '''
        global img_float

        if reset:
            self.reset_all() #打开一张新图之前先将各个参数都归位。当图像的修改方式为将 lut 应用后则不必进行该操作。


        img_float = colour.read_image(file_name)
        img = (img_float*255).astype(np.uint8)
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

    # def resizeEvent(self, event):
    #     '''
    #     根据窗口的大小来自适应调整图像大小
    #     死活不识别事件，暂且搁置
    #     '''
    #     global img_float
    #     print(123)
    #     view_size = self.ui.graphicsView.size()
    #     img_w, img_h = img_float.shape[1], img_float.shape[0]


    def brightness_edit(self, line= False):
        '''
        调整亮度
        '''
        # 真正用的时候应该是对 lut 而不是图像操作，这个 lut 应该是一个 numpy 数组或自己定义的对象

        if line: #如果是修改了edit line
            self.ui.brightnessSlider.setValue(int(float(self.ui.brightnessLineEdit.text())*100))

        global enhence_list
        value = self.ui.brightnessSlider.value()/100
        self.ui.brightnessLineEdit.setText(str(value))
        enhence_list[0] = value
        self.color_enhence()

    def contrast_edit(self, line= False):
        '''
        调整对比度
        '''
        if line: 
            self.ui.contrastSlider.setValue(int(float(self.ui.contrastLineEdit.text())*100))

        global enhence_list
        value = self.ui.contrastSlider.value()/100
        self.ui.contrastLineEdit.setText(str(value))
        enhence_list[1] = value
        self.color_enhence()
        
    def exposure_edit(self, line= False):
        '''
        调整曝光
        '''
        if line: 
            self.ui.exposureSlider.setValue(int(float(self.ui.exposureLineEdit.text())*100))

        global enhence_list
        value = self.ui.exposureSlider.value()/100
        self.ui.exposureLineEdit.setText(str(value))
        enhence_list[2] = value
        self.color_enhence()

    def saturation_edit(self, line= False):
        '''
        调整饱和度
        '''
        if line: 
            self.ui.saturationSlider.setValue(int(float(self.ui.saturationLineEdit.text())*100))

        global enhence_list
        value = self.ui.saturationSlider.value()/100
        self.ui.saturationLineEdit.setText(str(value))
        enhence_list[3] = value
        self.color_enhence()

    def vibrance_edit(self, line= False):
        '''
        调整自然饱和度
        '''
        if line: 
            self.ui.vibranceSlider.setValue(int(float(self.ui.vibranceLineEdit.text())*100))

        global enhence_list
        value = self.ui.vibranceSlider.value()/100
        self.ui.vibranceLineEdit.setText(str(value))
        enhence_list[4] = value
        self.color_enhence()

    def warmth_edit(self, line= False):
        '''
        调整色温
        '''
        if line: 
            self.ui.warmthSlider.setValue(int(float(self.ui.warmthLineEdit.text())*100))

        global enhence_list
        value = self.ui.warmthSlider.value()/100
        self.ui.warmthLineEdit.setText(str(value))
        enhence_list[5] = value
        self.color_enhence()

    def tint_edit(self, line= False):
        '''
        调整色调
        '''
        if line: 
            self.ui.tintSlider.setValue(int(float(self.ui.tintLineEdit.text())*100))

        global enhence_list
        value = self.ui.tintSlider.value()/100
        self.ui.tintLineEdit.setText(str(value))
        enhence_list[6] = value
        self.color_enhence()

    def color_enhence(self):
        '''
        完成一级校色
        '''
        global enhence_list
        self.hald_out = rgb_color_enhance(self.hald_img, brightness=enhence_list[0], contrast=enhence_list[1], exposure=enhence_list[2], saturation=enhence_list[3],vibrance=enhence_list[4],warmth=enhence_list[5],tint=enhence_list[6])

        self.show_img()



    def convert_cs(self):
        '''
        完成色域/白点/gamma 相关转换
        '''

        print(time.time())

        in_gamut = self.ui.inGamut.currentText()
        out_gamut = self.ui.outGamut.currentText()

        in_gamma = self.ui.inGamma.currentText()
        out_gamma = self.ui.outGamma.currentText()

        in_wp = self.ui.inWp.currentText()
        out_wp = self.ui.outWp.currentText()

        #等处理好了其它的再把 XYZ、HSV 这些加进来
        img_out = gamut_convert(in_gamut, out_gamut, self.hald_img, True, in_wp, out_wp)
        self.hald_out = gamma_convert(img_out, in_gamma, out_gamma)

        self.show_img()

    def show_img(self):
        '''
        将处理后的图片显示到 UI 上
        '''
        global img_float

        lut = compute_lut_np(self.hald_out.reshape(36**3, 3), 36)
        
        img_out = apply_lut_np(lut, img_float)


        frame = QImage(img_out, img_out.shape[1], img_out.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item.setPixmap(pix) 

        print(time.time())



    def reset_all(self):
        '''
        复位各个参数
        '''
        self.ui.brightnessSlider.setValue(0)
        self.ui.contrastSlider.setValue(0)
        self.ui.exposureSlider.setValue(0)
        self.ui.saturationSlider.setValue(0)
        self.ui.vibranceSlider.setValue(0)
        self.ui.warmthSlider.setValue(0)
        self.ui.tintSlider.setValue(0)

        self.ui.inGamut.setCurrentIndex(0)
        self.ui.inGamma.setCurrentIndex(0)
        self.ui.inWp.setCurrentIndex(0)
        self.ui.outGamut.setCurrentIndex(0)
        self.ui.outGamma.setCurrentIndex(0)
        self.ui.outWp.setCurrentIndex(0)

        

app = QApplication([])
app.setStyle('WindowsVista')
lut_ui = LutUI()
lut_ui.ui.show()
app.exec_()
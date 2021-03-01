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

from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QMessageBox, QInputDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QEvent, QObject
from PySide6.QtGui import QImage, QPixmap, QIcon
from MyWidget import myQGraphicsView
from MySignal import mysgn
from output_dialog import Output_Dialog


import colour
import numpy as np
import time
from lut import LUT
from lut_color_enhance import rgb_color_enhance
from lut_color_space import gamma_convert, gamut_convert
from generate_HALD import generate_HALD_np
from lut_compute import compute_lut_np
from lut_preview import apply_lut_np
from auto_wb import auto_wb_correct, auto_wb_correct_qcgp, auto_wb_srgb
import lut_IO


class LutUI(QObject):
    def __init__(self):
        
        super(LutUI, self).__init__()

        qfile_gui = QFile("Smart LUT Creator.ui")
        qfile_gui.open(QFile.ReadOnly)
        qfile_gui.close()

        loader = QUiLoader()
        loader.registerCustomWidget(myQGraphicsView)
        self.ui = loader.load(qfile_gui)
        self.ui.installEventFilter(self)
        self.ui.graphicsView.viewport().installEventFilter(self)
        self.ui.setWindowIcon(QIcon("icon.png"))


        self.ui.graphicsView.resize(654, 525) #resize事件一开始获得的大小不对，手动设一下

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

        #上面的一排按钮
        self.ui.addLutButton.clicked.connect(self.add_lut)
        self.ui.openLutButton.clicked.connect(self.read_lut)
        self.ui.saveLutButton.clicked.connect(self.save_lut)
        self.ui.exportLutButton.clicked.connect(self.export_lut)
        self.ui.exportImgButton.clicked.connect(self.export_img)
        self.ui.openImgButton.clicked.connect(self.img_window)
        self.ui.resizeLutButton.clicked.connect(self.resize_lut)

        #右下角的按钮
        self.ui.autoWbButton.clicked.connect(self.auto_wb)




        self.hald_img = generate_HALD_np(33)
        self.preview = None
        self.open_img('test_img/panel.jpg', reset = False)  #默认测试图片
        self.img_name = '未命名'

        self.lut = compute_lut_np(self.hald_img, 33, '未命名')
        self.lut_path = None
        self.ui.setWindowTitle("未命名"+ " - " + str(self.lut.cubeSize) + " - " + "Smart LUT Creator")







        

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
        openfile_name = QFileDialog.getOpenFileNames(self.ui, '选择图像文件', '.', "Image Files(*.jpg *.png *.tif *.tiff *.bmp)") #.代表是当前目录
        if openfile_name[0] == []: #如果用户什么也没选就什么也不做，不然下一步会报错
            return

        file_path = openfile_name[0][0]
        self.open_img(file_path)
        self.img_name = file_path.split('/')[-1][0:-4] #[0:-4]去扩展名

        

    def open_img(self, file_name, reset = True):
        '''
        输入图像
        '''
        global img_float

        if reset:
            self.reset_all() #打开一张新图之前先将各个参数都归位。当图像的修改方式为将 lut 应用后则不必进行该操作。


        img_float = colour.read_image(file_name)
        img = (img_float*255).astype(np.uint8)
        self.preview = img
        self.zoomscale=1  

        frame = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item = QGraphicsPixmapItem(pix) #创建像素图元
        self.scene = QGraphicsScene() #创建场景
        self.scene.addItem(self.item)
        # self.ui.graphicsView = myQGraphicsView()
        self.ui.graphicsView.setScene(self.scene) #将场景添加至视图

        self.adjust_zoom_size()                                                    

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


    def eventFilter(self, obj, event):
        '''
        处理不同事件
        '''
        # return 那里会报错，原因不明。QObject 和 super(LutUI, self).__init__() 也是为了处理事件才加上的

        if obj is self.ui:
            if event.type() == QEvent.Resize:
                self.adjust_zoom_size()


        if obj is self.ui.graphicsView.viewport():

            if event.type() == QEvent.DragMove: #Drop 捕获不到，先这样吧
                path = event.mimeData().text().replace('file:///', '') # 删除多余开头
                self.open_img(path)

            if event.type() == QEvent.MouseMove:
                if self.left_click:
                    self._endPos = event.pos() - self._startPos
                    move_x = self.scene.sceneRect().x() + self._endPos.x()
                    move_y = self.scene.sceneRect().y() + self._endPos.y()
                    self._startPos = event.pos()
                    # self.scene.setSceneRect(move_x, move_y, self.scene.sceneRect().width(), self.scene.sceneRect().height()) #以原点为中心移动
                    self.item.setPos(self.item.pos() + self._endPos)

            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.left_click = True
                    self._startPos = event.pos()

            if event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.left_click = False

            if event.type() == QEvent.Wheel:
                #为了以鼠标为中心进行缩放，就需要先缩放，再按照比例进行平移
                self.zoomscale=self.zoomscale+event.angleDelta().y()/1000
                if self.zoomscale<=0:
                    self.zoomscale=0.2
                if self.zoomscale>=5:
                    self.zoomscale=5
                self.item.setScale(self.zoomscale) 

                delta = event.scenePosition() - self.item.pos()  # 鼠标位置与图元左上角的差值
                ratio = self.zoomscale/(self.zoomscale-event.angleDelta().y()/1000)-1 # 对应缩放比例
                offset = delta * ratio
                self.item.setPos(self.item.pos() - offset)
                
        return super(LutUI, self).eventFilter(obj, event)

        


    def adjust_zoom_size(self):
        '''
        根据窗口的大小来自适应调整图像大小
        '''
        view_size = self.ui.graphicsView.size()
        view_w, view_h = view_size.width()-20, view_size.height()-20 #留出20像素滚动条
        img_w, img_h = img_float.shape[1], img_float.shape[0]
        zoomscale_w = view_w/img_w
        zoomscale_h = view_h/img_h
        if zoomscale_w < zoomscale_h:
            self.item.setScale(zoomscale_w) 
            self.zoomscale = zoomscale_w
        else:
            self.item.setScale(zoomscale_h) 
            self.zoomscale = zoomscale_h

        self.scene.setSceneRect(0, 0, img_w*zoomscale_w, img_h*zoomscale_h)

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
        hald_out = rgb_color_enhance(self.hald_img, brightness=enhence_list[0], contrast=enhence_list[1], exposure=enhence_list[2], saturation=enhence_list[3],vibrance=enhence_list[4],warmth=enhence_list[5],tint=enhence_list[6])
        self.lut = compute_lut_np(hald_out, self.lut.cubeSize, self.lut.name)

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
        img_out = gamut_convert(in_gamut, out_gamut, self.hald_img, False, True, in_wp, out_wp)
        img_out = np.clip(img_out, 0, 1)
        hald_out = gamma_convert(img_out, in_gamma, out_gamma)
        self.lut = compute_lut_np(hald_out, self.lut.cubeSize, self.lut.name)

        self.show_img()

    def show_img(self):
        '''
        将处理后的图片显示到 UI 上
        '''
        global img_float
        
        img_out = apply_lut_np(self.lut, img_float)
        self.preview = img_out


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


    def add_lut(self):
        value, ok = QInputDialog.getInt(self.ui, "新建 LUT", "请输入新建 LUT 大小（0~128）:", self.lut.cubeSize, 2, 65)
        if ok and value != self.lut.cubeSize:
            self.hald_img = generate_HALD_np(value)
            self.lut = compute_lut_np(self.hald_img, value, '未命名')
            self.lut_path = None
            self.lut.name = '未命名'
            self.ui.setWindowTitle(self.lut.name+ " - " + str(self.lut.cubeSize) + " - " + "Smart LUT Creator")
            self.reset_all()
            self.show_img()

    def read_lut(self):
        '''
        打开外部 LUT
        '''
        openfile_name = QFileDialog.getOpenFileNames(self.ui, '选择 LUT 文件', '.', 'All Files(*);;Davinci Cube(*.cube);;Nuke 3dl(*.3dl);;Lustre 3dl(*.3dl)') #.代表是当前目录
        if openfile_name[0] == []: 
            return

        file_path = openfile_name[0][0]
        self.lut_path = file_path
        ext_name = file_path.split('/')[-1].split('.')[-1].lower() #扩展名，最后统一转成小写

        if ext_name == 'cube':
            self.lut = lut_IO.FromCubeFile(file_path)
            self.load_lut()
           
        elif ext_name == '3dl':
            with open(file_path, 'rt') as f:
                lut_lines = f.readlines()
            count = 0
            for line in lut_lines:
                if line.startswith('#') or line=='\n':
                    continue
                count += 1
                if line.startswith('Mesh'):
                    self.lut = lut_IO.FromLustre3DLFile(file_path)
                    self.load_lut()
                    break
                if count == 20: #很暴力，遍历前20行非空行和非注释行，找到‘mesh’就是Lustre，找不到就是nuke
                    self.lut = lut_IO.FromNuke3DLFile(file_path)
                    self.load_lut()
                    break
        else:
            QMessageBox.information(self.ui, "抱歉", "尚不支持该格式", QMessageBox.Ok, QMessageBox.Ok)

    def load_lut(self):
        '''
        因为打开不同格式 lut 文件都会指向一些相同的操作，再单独用一个函数来处理
        '''
        self.hald_img = np.float64(apply_lut_np(self.lut, self.hald_img)/255) 
        self.show_img()
        self.ui.setWindowTitle(self.lut.name+ " - " + str(self.lut.cubeSize) + " - " + "Smart LUT Creator")
        self.outlut = self.lut #为了resize时可以保留外部lut对hald的修改，单独存一下该lut


    def save_lut(self):
        if self.lut_path:
            #如果有路径说明是已经存在的 lut 文件，直接覆盖保存
            self.export_lut(self.lut_path)
        else:
            #没有路径直接调用另存为
            self.export_lut()


    def export_lut(self, path=None):
        self.output_dialog = Output_Dialog()
        self.output_dialog.set_lut_name(self.lut.name)
        self.output_dialog.show()
        self.output_dialog.exec_()
        output_info = self.output_dialog.return_info()

        if path: #直接覆盖保存，目前只对 cube 支持较好
            save_path = path
            ext_name = save_path.split('/')[-1].split('.')[-1].lower() 

            if ext_name == 'cube':
                lut_IO.ToCubeFile(self.lut, save_path)
            elif ext_name == '3dl':
                lut_IO.ToNuke3DLFile(self.lut, save_path)
            # elif ext_name == '3dl':
            #     lut_IO.ToLustre3DLFile(self.lut, save_path)
        else: #正常导出
            if len(output_info) == 0: 
                return

            save_path = output_info[0]
            ext_name = output_info[1][1:]
            if ext_name == 'cube':
                lut_IO.ToCubeFile(self.lut, save_path)
            elif ext_name == '3dl':
                lut_type = output_info[2]
                lut_size = int(output_info[3])
                lut_depth = int(output_info[4][:2])

                self.lut = self.lut.Resize(lut_size, reanme = False)
                if lut_type == 'Lustre':
                    lut_IO.ToLustre3DLFile(self.lut, save_path, lut_depth)
                elif lut_type == 'Nuke':
                    lut_IO.ToNuke3DLFile(self.lut, save_path, lut_depth)


    def export_img(self):
        save_path = QFileDialog.getSaveFileName(self.ui, '导出当前预览', './'+self.img_name+'_已转换.png', 'png(*.png);;jpg(*.jpg);;tif(*.tif *.tiff);;bmp(*.bmp)')
        if save_path[0] == '': 
            return

        colour.write_image(self.preview, save_path[0])

    def resize_lut(self):
        value, ok = QInputDialog.getInt(self.ui, "修改尺寸", "请输入修改后的 LUT 大小:", self.lut.cubeSize, 2, 65)
        if ok:
            self.lut = self.lut.Resize(value)
            self.hald_img = generate_HALD_np(value)
            if hasattr(self, 'outlut'): #如果导入过外部 lut 的话单独处理
                self.hald_img = np.float64(apply_lut_np(self.outlut, self.hald_img)/255) 
            self.ui.setWindowTitle(self.lut.name+ " - " + str(self.lut.cubeSize) + " - " + "Smart LUT Creator")
            self.show_img()

    def auto_wb(self):
        global img_float
        # hald_out = auto_wb_correct(img_float, self.hald_img, self.ui.faceCheckBox.isChecked()) 
        # hald_out = auto_wb_correct_qcgp(img_float, self.hald_img) 
        hald_out = auto_wb_srgb(img_float, self.hald_img, self.ui.faceCheckBox.isChecked()) 
        self.lut = compute_lut_np(hald_out, self.lut.cubeSize, self.lut.name)
        self.show_img()




app = QApplication([])
app.setStyle('WindowsVista')
lut_ui = LutUI()
lut_ui.ui.show()
app.exec_()
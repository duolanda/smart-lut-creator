from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from colour import read_image, write_image
import numpy as np
import tps
import colorgram


class ColorMatch_Dialog(QDialog):
    
    out_hald_signel = Signal(object)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("色彩匹配")
        self.setWindowIcon(QIcon("icon.png"))
        
        self.resize(755, 558)

        self.setupUi(self)
        
        self.points = []
        
        self.sourceView.setStyleSheet("background: transparent;border:0px;")
        self.destinationView.setStyleSheet("background: transparent;border:0px;")
        self.outputView.setStyleSheet("background: transparent;border:0px;")
        
        self.sourceView.installEventFilter(self)
        
        self.sourceButton.clicked.connect(lambda: self.img_window('source'))
        self.destinationButton.clicked.connect(lambda: self.img_window('destination'))
        self.generateButton.clicked.connect(self.do_tps)
                
        

    def setupUi(self, Dialog):
        Dialog.setObjectName("centralwidget")
        self.verticalLayout_5 = QVBoxLayout(Dialog)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.sourceButton = QPushButton(Dialog)
        self.sourceButton.setObjectName("sourceButton")

        self.verticalLayout.addWidget(self.sourceButton)

        self.sourceView = QGraphicsView(Dialog)
        # self.sourceView = QLabel(Dialog)
        # self.sourceView.setObjectName("sourceView")

        self.verticalLayout.addWidget(self.sourceView)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.destinationButton = QPushButton(Dialog)
        self.destinationButton.setObjectName("destinationButton")

        self.verticalLayout_2.addWidget(self.destinationButton)

        self.destinationView = QGraphicsView(Dialog)
        self.destinationView.setObjectName("destinationView")

        self.verticalLayout_2.addWidget(self.destinationView)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 3)

        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(20, 89, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName("label_3")

        self.verticalLayout_3.addWidget(self.label_3)

        self.outputView = QGraphicsView(Dialog)
        self.outputView.setObjectName("outputView")

        self.verticalLayout_3.addWidget(self.outputView)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.label = QLabel(Dialog)
        self.label.setObjectName("label")

        self.verticalLayout_4.addWidget(self.label)

        self.horizontalSlider = QSlider(Dialog)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setMaximum(6)
        self.horizontalSlider.setValue(3)
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.verticalLayout_4.addWidget(self.horizontalSlider)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_3)

        self.generateButton = QPushButton(Dialog)
        self.generateButton.setObjectName("generateButton")

        self.verticalLayout_4.addWidget(self.generateButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 3)

        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.verticalLayout_5.setStretch(0, 5)
        self.verticalLayout_5.setStretch(1, 1)
        self.verticalLayout_5.setStretch(2, 5)

        self.retranslateUi()


    def retranslateUi(self):
        self.sourceButton.setText("选择原图")
        self.destinationButton.setText("选择目标图")
        self.label_3.setText("结果预览")
        self.label.setText("平滑度")
        self.generateButton.setText("生成LUT")


    def img_window(self, view):
        
        openfile_name = QFileDialog.getOpenFileNames(self, '选择图像文件', '.', "Image Files(*.jpg *.jpeg *.png *.tif *.tiff *.bmp)") 
        if openfile_name[0] == []: 
            return

        file_path = openfile_name[0][0]
        self.open_img(file_path, view)

    def open_img(self, file_name, view):
        
        if(view == 'source'):
            self.src_path = file_name
            self.src = read_image(file_name)
            img = (self.src*255).astype(np.uint8)
            
            self.points = []
            
            self.height = self.src.shape[0]
            self.width = self.src.shape[1]

            frame = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)
            pix = QPixmap.fromImage(frame)
        
            self.source_item = QGraphicsPixmapItem(pix) 
            self.source_scene = QGraphicsScene()
            self.source_scene.addItem(self.source_item)
            self.sourceView.setScene(self.source_scene) 
            
            self.adjust_zoom_size(self.sourceView, self.source_item, self.source_scene)
            
        elif(view == 'destination'):
            self.dst_path = file_name
            self.dst = read_image(file_name)
            img = (self.dst*255).astype(np.uint8)

            frame = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)
            pix = QPixmap.fromImage(frame)
        
            self.destination_item = QGraphicsPixmapItem(pix) 
            self.destination_scene = QGraphicsScene()
            self.destination_scene.addItem(self.destination_item)
            self.destinationView.setScene(self.destination_scene) 
            
            self.adjust_zoom_size(self.destinationView, self.destination_item, self.destination_scene)
        
        
    def adjust_zoom_size(self, view, item, scene):

        view_size = view.size()
        view_w, view_h = view_size.width(), view_size.height() 
        img_w, img_h = self.src.shape[1], self.src.shape[0]
        zoomscale_w = view_w/img_w
        zoomscale_h = view_h/img_h
        if zoomscale_w < zoomscale_h:
            item.setScale(zoomscale_w) 
            self.zoomscale = zoomscale_w
        else:
            item.setScale(zoomscale_h) 
            self.zoomscale = zoomscale_h

        scene.setSceneRect(0, 0, img_w*zoomscale_w, img_h*zoomscale_h)
        
        self.zoomscale_w = zoomscale_w
        self.zoomscale_h = zoomscale_h
    
    def do_tps(self):
        src = self.src
        dst = self.dst
        points = np.array(self.points)
        points = [list(points[:,0]), list(points[:,1])]
        
        height = self.height
        width = self.width
        
        src_pts = src[points]
        dst_pts = dst[points]
        
        
        # n=20
        # src_color = colorgram.extract(self.src_path, n)
        # tar_color = colorgram.extract(self.dst_path, n)
        # src_pts=np.zeros((n,3),dtype=np.float)
        # for i,c in enumerate(src_color):
        #     src_pts[i,:]=np.asarray(c.rgb[:],dtype=np.float)/255.0
        # dst_pts=np.zeros((n,3),dtype=np.float)
        # for i,c in enumerate(tar_color):
        #     dst_pts[i,:]=np.asarray(c.rgb[:],dtype=np.float)/255.0
            
        # src_pts=np.sort(src_pts,axis=0)
        # dst_pts=np.sort(dst_pts,axis=0) 
        
        
        # trans = tps.TPS(src_pts, dst_pts, lambda_ = self.horizontalSlider.value())
        trans = tps.TPS(src_pts, dst_pts, lambda_ = 100)
        # output = trans(src.reshape(height*width, 3))
        # output = output.reshape(height, width, 3)
        # output *=255
        # output +=255
        # output =np.int_(output)
        # output %=256
        # output =output.astype(np.uint8)
        # write_image(output, 'abc.jpg')
        
        out_hald = trans(self.hald.reshape(self.hald.shape[0]*self.hald.shape[1], 3))
        out_hald = out_hald.reshape(self.hald.shape[0], self.hald.shape[1], 3)
        self.out_hald_signel.emit(out_hald)


        # STEP = 17
        # samples = np.linspace(0, 1, STEP)
        # rr, gg, bb = np.meshgrid(samples, samples, samples)
        # source_lut = np.stack([rr, gg, bb], axis=3)
        # source_lut = source_lut.transpose((2, 0, 1, 3)).reshape(-1, 3)
        # dst_lut = trans(source_lut)
        # lut_file = 'lut.cube'
        # lut_string = 'TITLE \"Generated by Foundry::LUT\"\nLUT_3D_SIZE 17\n'
        # lut_string += '\n'.join([' '.join([str(c) for c in row])
        #                     for row in dst_lut.tolist()])
        # with open(lut_file, 'w') as f:
        #     f.write(lut_string)

    def eventFilter(self, obj, event):
        '''
        处理不同事件
        '''
        if event.type() == QEvent.Resize:
            self.adjust_zoom_size(self.sourceView, self.source_item, self.source_scene)
            self.adjust_zoom_size(self.destinationView, self.destination_item, self.destination_scene)
                
        if obj is self.sourceView:
            if event.type() == QEvent.MouseButtonPress:
                x = event.pos().x()
                y = event.pos().y()

                self.source_scene.addEllipse(x-5, y-5, 10, 10, QPen(QColor(234, 125, 80)))
                raw_x = int(x/self.zoomscale_w)
                raw_y = int(y/self.zoomscale_h)
                if raw_x > self.width:
                    raw_x = self.width-1
                if raw_x < 0:
                    raw_x = 0
                if raw_y > self.height:
                    raw_y = self.height-1
                if raw_y < 0:
                    raw_y = 0
                self.points.append([raw_y, raw_x])
                
    def set_hald(self, hald_img):
        self.hald = hald_img
    
    def get_img(self):
        return self.src
    
    def show_preview(self, output):
        frame = QImage(output, output.shape[1], output.shape[0], output.shape[1]*3, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        item = QGraphicsPixmapItem(pix) 
        scene = QGraphicsScene()
        scene.addItem(item)
        self.outputView.setScene(scene) 
        self.adjust_zoom_size(self.outputView, item, scene)
        
if __name__ == '__main__':
    app = QApplication()
    window = ColorMatch_Dialog()
    window.show()
    app.exec_()
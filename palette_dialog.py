from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QIcon, QImage, QPixmap
import colorgram
import numpy as np
from PIL import Image

class Palette_Dialog(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('色板')
        self.setWindowIcon(QIcon("icon.png"))
        self.height = 150
        self.width = 900
        self.resize(self.width, self.height)

        self.init_widgets()


    def init_widgets(self):
        self.label_pic = QLabel()
        self.label_pic.setScaledContents(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_pic)

        self.setLayout(vbox)
        # self.adjustSize()


    def palette_extract(self, color_number):
        img = Image.fromarray(self.img) # colorgram 需要传入 PIL 格式的图片或文件名
        colors = colorgram.extract(img, color_number)

        height = self.height
        width = self.width
        output = np.zeros((height, width, 3), dtype='uint8')

        edge = 0
        for color in colors:
            output[0:height, edge:edge+int(width*color.proportion)] = np.asarray(color.rgb)
            edge = edge+int(width*color.proportion)

        img = QImage(output, output.shape[1], output.shape[0], output.shape[1]*3, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.label_pic.setPixmap(pix)


    def set_img(self, img):
        self.img = img



# if __name__ == '__main__':
#     app = QApplication()
#     window = Palette_Dialog()
#     window.show()
#     app.exec_()
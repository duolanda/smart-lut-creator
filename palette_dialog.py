from PySide6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtGui import QIcon, QImage, QPixmap
import colorgram
import numpy as np
from PIL import Image


def rgb_to_hex(rgb):
        return ('#%02x%02x%02x' %rgb)

class Palette_Dialog(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('色板')
        self.setWindowIcon(QIcon("icon.png"))
        self.height = 150
        self.width = 900
        self.resize(self.width, self.height)


    def gen_color_button(self, color_list):

        hbox = QHBoxLayout()

        self.button_list = []
        for color in color_list:
            color_inverse = [255-i for i in color] #标识色号的文字用反色，保证看清
            color_hex = rgb_to_hex(tuple(color))

            button = QPushButton()
            button.setFixedSize(self.width/len(color_list), self.height)
            button.setText(str(color)[1:-1] + '\n' + color_hex)
            button.setStyleSheet('QPushButton{background:rgb(%s); border-radius:5px; color:rgb(%s)} QPushButton:hover{border-color:red;}' %(str(color)[1:-1], str(color_inverse)[1:-1]))

            # button.clicked.connect(lambda :self.push(self.sender()))

            hbox.addWidget(button)

            self.button_list.append(button)

        self.setLayout(hbox)     

    def push(self,n):
        print(n)


    def palette_extract(self, color_number):
        img = Image.fromarray(self.img) # colorgram 需要传入 PIL 格式的图片或文件名
        colors_ex = colorgram.extract(img, color_number)
        colors =[list(color.rgb) for color in colors_ex]

        self.gen_color_button(colors)


    def set_img(self, img):
        self.img = img



if __name__ == '__main__':
    app = QApplication()

    window = Palette_Dialog()
    img = np.array(Image.open('test_img/panel.jpg'))
    window.set_img(img)
    window.palette_extract(6)

    window.show()
    app.exec_()
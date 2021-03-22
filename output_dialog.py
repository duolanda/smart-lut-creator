import os
import PySide6
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Output_Dialog(QDialog):
    def __init__(self):
        super(Output_Dialog, self).__init__()
        self.setWindowIcon(QIcon("icon.png"))
        self.setupUi(self)

        self.formatComboBox.currentIndexChanged.connect(self.display)
        self.filePathPushButton.clicked.connect(self.select_file)
        self.okPushButton.clicked.connect(self.export)


    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("outputDialog")
        Dialog.setWindowTitle("LUT 导出")
        Dialog.resize(400, 300)

        self.ext = '.cube'
        self.output_info = []

        self.label = QLabel(Dialog)
        self.label.setObjectName("label")
        self.label.setText("存储路径")

        self.filePathLineEdit = QLineEdit(Dialog)
        self.filePathLineEdit.setObjectName("filePathLineEdit")

        self.filePathPushButton = QPushButton(Dialog)
        self.filePathPushButton.setObjectName("filePathPushButton")
        self.filePathPushButton.setText("浏览")


        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("文件格式")

        self.formatComboBox = QComboBox(Dialog)
        self.formatComboBox.addItem("Cube LUT (.cube)")
        self.formatComboBox.addItem("Autodesk 3D LUT (.3dl)")
        self.formatComboBox.setObjectName("formatComboBox")

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.okPushButton = QPushButton()
        self.okPushButton.setObjectName("okPushButton")
        self.okPushButton.setText("导出")


        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")


        self.horizontalLayout.addWidget(self.label)
        self.horizontalLayout.addWidget(self.filePathLineEdit)
        self.horizontalLayout.addWidget(self.filePathPushButton)
        self.horizontalLayout_2.addWidget(self.label_2)
        self.horizontalLayout_2.addWidget(self.formatComboBox)
        self.horizontalLayout_6.addItem(self.horizontalSpacer)
        self.horizontalLayout_6.addWidget(self.okPushButton)

        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack1UI()
        self.stack2UI()
        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)

        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.Stack)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.setLayout(self.verticalLayout)

        
    
    def stack1UI(self):
        self.ext = '.cube'

        hbox = QHBoxLayout() #其实这里不用放什么东西，这里就占个位
        self.stack1.setLayout(hbox)


        file_name = self.filePathLineEdit.text()
        file_name = file_name.split('.')
        file_name[-1] = self.ext[1:]
        self.filePathLineEdit.setText('.'.join(file_name))
    
    def stack2UI(self):
        self.ext = '.3dl'

        self.label_3 = QLabel()
        self.label_3.setObjectName("label_3")
        self.label_3.setText("类型")

        self.typeComboBox = QComboBox()
        self.typeComboBox.setObjectName("typeComboBox")
        self.typeComboBox.addItem("Lustre")
        self.typeComboBox.addItem("Nuke")
        self.typeComboBox.currentIndexChanged.connect(self.change_3dl_option)

        self.label_4 = QLabel()
        self.label_4.setObjectName("label_4")
        self.label_4.setText("尺寸")

        self.sizeComboBox = QComboBox()
        self.sizeComboBox.setObjectName("sizeComboBox")
        self.sizeComboBox.addItem("17")
        self.sizeComboBox.addItem("33")
        self.sizeComboBox.addItem("65")


        self.label_5 = QLabel()
        self.label_5.setObjectName("label_5")
        self.label_5.setText("输出深度")

        self.depthComboBox = QComboBox()
        self.depthComboBox.setObjectName("depthComboBox")
        self.depthComboBox.addItem("12-bit")
        self.depthComboBox.addItem("16-bit")


        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        vbox = QVBoxLayout()

        self.horizontalLayout_3.addWidget(self.label_3)
        self.horizontalLayout_3.addWidget(self.typeComboBox)
        self.horizontalLayout_4.addWidget(self.label_4)
        self.horizontalLayout_4.addWidget(self.sizeComboBox)
        self.horizontalLayout_5.addWidget(self.label_5)
        self.horizontalLayout_5.addWidget(self.depthComboBox)

        vbox.addLayout(self.horizontalLayout_3)
        vbox.addLayout(self.horizontalLayout_4)
        vbox.addLayout(self.horizontalLayout_5)

        self.stack2.setLayout(vbox)


        file_name = self.filePathLineEdit.text()
        file_name = file_name.split('.')
        file_name[-1] = self.ext[1:]
        self.filePathLineEdit.setText('.'.join(file_name))

            

    def change_3dl_option(self):
        if self.typeComboBox.currentText() == "Lustre":
            self.sizeComboBox.clear()
            self.sizeComboBox.addItem("17")
            self.sizeComboBox.addItem("33")
            self.sizeComboBox.addItem("65")

        elif self.typeComboBox.currentText() == "Nuke":
            self.sizeComboBox.clear()
            self.sizeComboBox.addItem("32")
            self.sizeComboBox.addItem("64")

    def select_file(self):
        name =self.lut_name
        self.output_path = QFileDialog.getSaveFileName(self, '选择 LUT 存储路径', './'+ name + self.ext)
        self.filePathLineEdit.setText(self.output_path[0])

    def set_lut_name(self, name):
        self.lut_name = name
        self.filePathLineEdit.setText(os.environ['USERPROFILE']+ '\\' + self.lut_name +".cube") #其实这里斜杠全是反的，以后再改吧

    def export(self):

        file_path = self.filePathLineEdit.text()
        file_ext = self.ext

        if self.ext == ".cube":
            self.output_info = [file_path, file_ext]
            

        elif self.ext == ".3dl":
            file_type = self.typeComboBox.currentText()
            file_size = self.sizeComboBox.currentText()
            file_depth = self.depthComboBox.currentText()
            self.output_info = [file_path, file_ext, file_type, file_size, file_depth]

        self.close()

    def return_info(self):
        return self.output_info

    def display(self,i):
        self.Stack.setCurrentIndex(i)        


if __name__ == '__main__':
    app = QApplication()
    window = Output_Dialog()
    window.show()
    app.exec_()
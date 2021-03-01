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
        self.setupUi(self)

        self.formatComboBox.currentIndexChanged.connect(self.change_element)
        self.filePathPushButton.clicked.connect(self.select_file)


    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("outputDialog")
        Dialog.setWindowTitle("LUT 导出")
        Dialog.resize(400, 300)

        self.ext = '.cube'

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

        self.okPushButton = QPushButton(Dialog)
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
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        QMetaObject.connectSlotsByName(Dialog)

    def change_element(self):
        if self.formatComboBox.currentText() == "Cube LUT (.cube)":
            self.ext = '.cube'

            Dialog = self

            if self.more_option:
                for i in reversed(range(self.horizontalLayout_3.count())): 
                    self.horizontalLayout_3.itemAt(i).widget().setParent(None)
                for i in reversed(range(self.horizontalLayout_4.count())): 
                    self.horizontalLayout_4.itemAt(i).widget().setParent(None)
                for i in reversed(range(self.horizontalLayout_5.count())): 
                    self.horizontalLayout_5.itemAt(i).widget().setParent(None)



        elif self.formatComboBox.currentText() == "Autodesk 3D LUT (.3dl)":
            self.ext = '.3dl'
            Dialog = self
            self.verticalLayout.removeItem(self.horizontalLayout_6)

            self.label_3 = QLabel(Dialog)
            self.label_3.setObjectName("label_3")
            self.label_3.setText("类型")

            self.typeComboBox = QComboBox(Dialog)
            self.typeComboBox.setObjectName("typeComboBox")
            self.typeComboBox.addItem("Lustre")
            self.typeComboBox.addItem("Nuke")
            self.typeComboBox.currentIndexChanged.connect(self.change_option)

            self.label_4 = QLabel(Dialog)
            self.label_4.setObjectName("label_4")
            self.label_4.setText("尺寸")

            self.sizeComboBox = QComboBox(Dialog)
            self.sizeComboBox.setObjectName("sizeComboBox")
            self.sizeComboBox.addItem("17")
            self.sizeComboBox.addItem("33")
            self.sizeComboBox.addItem("65")


            self.label_5 = QLabel(Dialog)
            self.label_5.setObjectName("label_5")
            self.label_5.setText("输出深度")

            self.depthComboBox = QComboBox(Dialog)
            self.depthComboBox.setObjectName("depthComboBox")
            self.depthComboBox.addItem("12-bit")
            self.depthComboBox.addItem("16-bit")


            self.horizontalLayout_3 = QHBoxLayout()
            self.horizontalLayout_3.setObjectName("horizontalLayout_3")
            self.horizontalLayout_4 = QHBoxLayout()
            self.horizontalLayout_4.setObjectName("horizontalLayout_4")
            self.horizontalLayout_5 = QHBoxLayout()
            self.horizontalLayout_5.setObjectName("horizontalLayout_5")

            self.horizontalLayout_3.addWidget(self.label_3)
            self.horizontalLayout_3.addWidget(self.typeComboBox)
            self.horizontalLayout_4.addWidget(self.label_4)
            self.horizontalLayout_4.addWidget(self.sizeComboBox)
            self.horizontalLayout_5.addWidget(self.label_5)
            self.horizontalLayout_5.addWidget(self.depthComboBox)
            self.verticalLayout.addLayout(self.horizontalLayout_3)
            self.verticalLayout.addLayout(self.horizontalLayout_4)
            self.verticalLayout.addLayout(self.horizontalLayout_5)

            self.verticalLayout.addLayout(self.horizontalLayout_6)

            self.more_option = True

        file_name = self.filePathLineEdit.text()
        file_name = file_name.split('.')
        file_name[-1] = self.ext[1:]
        self.filePathLineEdit.setText('.'.join(file_name))

    def change_option(self):
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
        name = "123" #原来是等于 self.lut.name
        self.output_path = QFileDialog.getSaveFileName(self, '选择 LUT 存储路径', './'+ name + self.ext)
        self.filePathLineEdit.setText(self.output_path[0])

    def set_lut_name(self, name):
        self.lut_name = name
        self.filePathLineEdit.setText(os.environ['USERPROFILE']+ '\\' + self.lut_name +".cube") #其实这里斜杠全是反的，以后再改吧


if __name__ == '__main__':
    app = QApplication()
    window = Output_Dialog()
    window.show()
    app.exec_()
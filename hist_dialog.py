import numpy as np

from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter, QColor, QPolygonF, QPainterPath, QBrush


class Hist_Dialog(QWidget):
    def __init__(self, size=200):
        super().__init__()
        self.setWindowIcon(QIcon("icon.png"))

        self.setWindowTitle('直方图')
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumSize(size, 100)

        self.init_widgets()

        self.sourceCheckBox.stateChanged.connect(self.change_option)
        self.rCheckBox.stateChanged.connect(self.change_option)
        self.gCheckBox.stateChanged.connect(self.change_option)
        self.bCheckBox.stateChanged.connect(self.change_option)

    def init_widgets(self):
        self.label_hist = QLabel()
        self.label_hist.setScaledContents(True)
        self.label_hist.setFocusPolicy(Qt.ClickFocus)
        self.setStyleSheet("QListWidget{border: 0px; font-size: 12px}")

        self.sourceCheckBox = QCheckBox("source")
        self.rCheckBox = QCheckBox("red")
        self.gCheckBox = QCheckBox("green")
        self.bCheckBox = QCheckBox("blue")

        self.sourceCheckBox.setChecked(False)
        self.rCheckBox.setChecked(True)
        self.gCheckBox.setChecked(True)
        self.bCheckBox.setChecked(True)


        # layout
        h = QHBoxLayout()
        h.addWidget(self.sourceCheckBox)
        h.addWidget(self.rCheckBox)
        h.addWidget(self.gCheckBox)
        h.addWidget(self.bCheckBox)
        h.setStretch(0, 3)
        h.setStretch(1, 1)
        h.setStretch(2, 1)
        h.setStretch(3, 1)

        vl = QVBoxLayout()
        vl.addWidget(self.label_hist)
        vl.addLayout(h)
        vl.setContentsMargins(0, 0, 0, 2)  # left, top, right, bottom
        self.setLayout(vl)
        self.adjustSize()


    def change_option(self):
        source = self.sourceCheckBox.isChecked()
        r = self.rCheckBox.isChecked()
        g = self.gCheckBox.isChecked()
        b = self.bCheckBox.isChecked()

        chans = []
        chan_colors = []
        i = 0
        if r == True:
            chans.append(0)
            chan_colors.append(QColor(255, 0, 0))
        if g == True:
            chans.append(1)
            chan_colors.append(QColor(0, 255, 0))
        if b == True:
            chans.append(2)
            chan_colors.append(QColor(10, 10, 255))

        if source:
            hist = histogram(self.s_img, chans=chans)
        else:
            hist = histogram(self.c_img, chans=chans)
        self.change_hist(hist)


    def change_hist(self, target_hist):
        pix = QPixmap.fromImage(target_hist)
        hist = pix.scaled(self.label_hist.width(), self.label_hist.height())
        self.label_hist.setPixmap(hist)

    def set_img(self, source_img, current_img):
        self.s_img = source_img
        self.c_img = current_img


def histogram(in_img, size=QSize(200, 200), bg_color=QColor(53, 53, 53), range=(0, 255),
                  chans=[0, 1, 2], chan_colors=[QColor(255, 0, 0), QColor(0, 255, 0), QColor(10, 10, 255)], clipping_threshold=0.02):
       
    binCount = 85  # 255 = 85 * 3

    # 缩放因子
    spread = float(range[1] - range[0])
    scale = size.width() / spread
    # 最后一个 bin 画起来是一根垂直线（宽度为0），需要修正缩放
    # 不修正的话窗口会填不满
    scale *= binCount / (binCount - 1)

    def drawChannelHistogram(painter, hist, bin_edges, color):
        '''
        单独绘制每个通道的直方图
        - painter：QPainter
        - hist：要绘制的直方图
        - bin_edges：每个 bin 的边缘
        - color：绘图颜色
        '''

        # 原来用的是 M = max(hist[1: ])，原因是为了强调重要数值，将第一个值去掉
        M = max(hist)  # 最大值作为其他 bin 的最高高度基准
        imgH = size.height()
        # 绘制梯形而不是矩形，以快速“平滑”直方图，最右边的梯形未绘制
        poly = QPolygonF()
        poly.append(QPointF(range[0], imgH))  # 左下角的点（QT的坐标原点是左上角）
        for i, y in enumerate(hist):
            try:
                h = imgH * y / M
                if np.isnan(h):
                    raise ValueError
            except (ValueError, ArithmeticError, FloatingPointError, ZeroDivisionError):
                return
            poly.append(QPointF((bin_edges[i] - range[0]) * scale, max(imgH - h, 0))) #y正方向是向下，所以要 imgH-h
            # indicator 裁切
            if i == 0 or i == len(hist)-1:
                left = bin_edges[0 if i == 0 else -1] * scale
                left = left - (20 if i > 0 else 0)  # 偏移右侧坐标
                percent = hist[i] * (bin_edges[i+1]-bin_edges[i])
                if percent > clipping_threshold:
                    # 根据 percent 值设定 indicator 的颜色
                    gPercent = min(1, np.clip((0.05 - percent) / 0.03, 0, 1))
                    painter.fillRect(left, 0, 10, 10, QColor(255, 255*gPercent, 0))
        # 填充颜色
        poly.append(QPointF(poly.constLast().x(), imgH))  # 右下角的点
        path = QPainterPath()
        path.addPolygon(poly)
        path.closeSubpath() #自动连到原点
        painter.setPen(Qt.NoPen) #只填充不描边
        painter.fillPath(path, QBrush(color))
    # drawChannelHistogram 函数结束

    buf = None
    buf = (in_img*255).astype(np.uint8)
    
    img = QImage(size.width(), size.height(), QImage.Format_ARGB32)
    img.fill(bg_color)
    qp = QPainter(img)
    if type(chan_colors) is QColor or type(chan_colors) is Qt.GlobalColor:
        chan_colors = [chan_colors]*3

    # 计算直方图
    # 如果 bins='auto'，有时会造成 bin 数过多( >= 10**9)或内存错误，所以不用

    hist_L, bin_edges_L = [0]*len(chans), [0]*len(chans)
    for i, ch in enumerate(chans):
        buf0 = buf[:, :, ch]
        hist_L[i], bin_edges_L[i] = np.histogram(buf0, range=range, bins=binCount, density=True)
        drawChannelHistogram(qp, hist_L[i], bin_edges_L[i], chan_colors[ch])
        
    qp.end()
    return img







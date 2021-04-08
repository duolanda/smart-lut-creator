import colour
import matplotlib.pyplot as plt
import numpy as np

import PySide6
from PySide6 import QtCore
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QListWidget, QListWidgetItem
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter, QColor, QPolygonF, QPainterPath, QBrush


class histForm(QWidget):
    """
    Form for histogram viewing
    """
    def __init__(self, size=200):
        super().__init__()
        self.mode = 'Luminosity'
        self.chanColors = [Qt.gray]
        self.setWindowTitle('Histogram')
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumSize(size, 100)
        self.Label_Hist = QLabel()
        self.Label_Hist.setScaledContents(True)
        self.Label_Hist.setFocusPolicy(Qt.ClickFocus)
        self.setStyleSheet("QListWidget{border: 0px; font-size: 12px}")

        # options
        # options1, optionNames1 = ['Original Image'], ['Source']
        # self.listWidget1 = optionsWidget(options=options1, optionNames=optionNames1, exclusive=False)
        # self.listWidget1.setFixedSize((self.listWidget1.sizeHintForColumn(0) + 15) * len(options1), 20)
        # options2, optionNames2 = ['R', 'G', 'B', 'L'], ['R', 'G', 'B', 'L']
        # self.listWidget2 = optionsWidget(options=options2, optionNames=optionNames2, exclusive=False, flow=optionsWidget.LeftToRight)
        # self.listWidget2.setFixedSize((self.listWidget2.sizeHintForRow(0) + 20) * len(options2), 20)  # + 20 needed to prevent scroll bar on ubuntu
        # # default: show color hists only
        # for i in range(3):
        #     self.listWidget2.checkOption(self.listWidget2.intNames[i])
        # self.options = UDict((self.listWidget1.options, self.listWidget2.options))



        # layout
        # h = QHBoxLayout()
        # h.setContentsMargins(0, 0, 0, 2)
        # h.addStretch(1)
        # h.addWidget(self.listWidget1)
        # h.addStretch(1)
        # h.addWidget(self.listWidget2)
        # h.addStretch(1)
        vl = QVBoxLayout()
        vl.addWidget(self.Label_Hist)
        # vl.addLayout(h)
        vl.setContentsMargins(0, 0, 0, 2)  # left, top, right, bottom
        self.setLayout(vl)
        self.adjustSize()

    def change_hist(self, target_hist):
        # img = QImage(target_hist, target_hist.shape[1], target_hist.shape[0], target_hist.shape[1]*3, QImage.Format_RGB888)
        pix = QPixmap.fromImage(target_hist)
        hist = pix.scaled(self.Label_Hist.width(), self.Label_Hist.height())
        self.Label_Hist.setPixmap(hist)



def histogram(in_img, size=QSize(200, 200), bgColor=Qt.white, range=(0, 255),
                  chans=[0, 1, 2], chanColors=[QColor(255, 0, 0), QColor(0, 255, 0), QColor(10, 10, 255)], clipping_threshold=0.02):
       
    binCount = 85  # 255 = 85 * 3
    # convert size to QSize
    if type(size) is int:
        size = QSize(size, size)
    # scaling factor for bin drawing
    spread = float(range[1] - range[0])
    scale = size.width() / spread
    # the last bin is drawn as a vertical line (width = 0),
    # so we correct the scale factor accordingly
    scale *= binCount / (binCount - 1)

    # per channel histogram function
    def drawChannelHistogram(painter, hist, bin_edges, color):
        # Draw histogram for a single channel.
        # param painter: QPainter
        # param hist: histogram to draw
        # smooth the histogram (first and last bins excepted) for a better visualization of clipping.
        # hist = np.concatenate(([hist[0]], SavitzkyGolayFilter.filter(hist[1:-1]), [hist[-1]]))
        # To emphasize significant values we clip the first bin to max height of the others
        M = max(hist[1: ])  # max(hist)  # max(hist[1:-1])
        imgH = size.height()
        # drawing  trapezia instead of rectangles to quickly "smooth" the histogram
        # the rightmost trapezium is not drawn
        poly = QPolygonF()
        poly.append(QPointF(range[0], imgH))  # bottom left point
        for i, y in enumerate(hist):
            try:
                h = imgH * y / M
                if np.isnan(h):
                    raise ValueError
            except (ValueError, ArithmeticError, FloatingPointError, ZeroDivisionError):
                # don't draw the histogram for this channel if M is too small
                return
            poly.append(QPointF((bin_edges[i] - range[0]) * scale, max(imgH - h, 0)))
            # clipping indicators
            if i == 0 or i == len(hist)-1:
                left = bin_edges[0 if i == 0 else -1] * scale
                left = left - (20 if i > 0 else 0)  # shift the indicator at right
                percent = hist[i] * (bin_edges[i+1]-bin_edges[i])
                if percent > clipping_threshold:
                    # set the color of the indicator according to percent value
                    nonlocal gPercent
                    gPercent = min(gPercent, np.clip((0.05 - percent) / 0.03, 0, 1))
                    painter.fillRect(left, 0, 10, 10, QColor(255, 255*gPercent, 0))
        # draw the filled polygon
        poly.append(QPointF(poly.constLast().x(), imgH))  # bottom right point
        path = QPainterPath()
        path.addPolygon(poly)
        path.closeSubpath()
        painter.setPen(Qt.NoPen)
        painter.fillPath(path, QBrush(color))
    # end of drawChannelHistogram

    # green percent for clipping indicators
    gPercent = 1.0
    buf = None
    buf = (in_img*255).astype(np.uint8)
    
    # drawing the histogram onto img
    img = QImage(size.width(), size.height(), QImage.Format_ARGB32)
    img.fill(bgColor)
    qp = QPainter(img)
    if type(chanColors) is QColor or type(chanColors) is Qt.GlobalColor:
        chanColors = [chanColors]*3
    # compute histograms
    # bins='auto' sometimes causes a huge number of bins ( >= 10**9) and memory error
    # even for small data size (<=250000), so we don't use it.

    hist_L, bin_edges_L = [0]*len(chans), [0]*len(chans)
    for i, ch in enumerate(chans):
        buf0 = buf[:, :, ch]
        hist_L[i], bin_edges_L[i] = np.histogram(buf0, range=range, bins=binCount, density=True)
        drawChannelHistogram(qp, hist_L[i], bin_edges_L[i], chanColors[ch])
        
    qp.end()
    return img


if __name__ == '__main__':
    app = QApplication()
    window = histForm()


    img = colour.read_image('G:/Documents/大学/毕设相关/smart-lut-creator/test_img/lena_std.tif')
    hist = histogram(img)
    # out = np.asarray(hist.bits())
    # out = out.reshape(200,200,4)
    # colour.write_image(out, 'out.png')
    window.change_hist(hist)


    window.show()
    app.exec_()





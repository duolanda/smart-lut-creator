import numpy as np

import PySide6
from PySide6 import QtCore
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QWidget, QListWidget, QListWidgetItem
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter, QColor, QPolygonF, QPainterPath, QBrush


class Hist_Dialog(QWidget):
    """
    Form for histogram viewing
    """
    def __init__(self, size=200):
        super().__init__()
        self.mode = 'Luminosity'
        self.chan_colors = [Qt.gray]
        self.setWindowTitle('Histogram')
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
    img.fill(bg_color)
    qp = QPainter(img)
    if type(chan_colors) is QColor or type(chan_colors) is Qt.GlobalColor:
        chan_colors = [chan_colors]*3
    # compute histograms
    # bins='auto' sometimes causes a huge number of bins ( >= 10**9) and memory error
    # even for small data size (<=250000), so we don't use it.

    hist_L, bin_edges_L = [0]*len(chans), [0]*len(chans)
    for i, ch in enumerate(chans):
        buf0 = buf[:, :, ch]
        hist_L[i], bin_edges_L[i] = np.histogram(buf0, range=range, bins=binCount, density=True)
        drawChannelHistogram(qp, hist_L[i], bin_edges_L[i], chan_colors[ch])
        
    qp.end()
    return img







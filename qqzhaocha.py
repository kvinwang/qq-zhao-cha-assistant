# coding:utf8
__author__ = 'loong'

from PySide import QtGui, QtCore
import ImageGrab
from StringIO import StringIO

import win32gui
import win32api
import win32con


def log(s):
    print(s)


class WindowConfig:
    WIDTH = 498             # 图宽
    HEIGHT = 448            # 图高
    ANCHOR_LEFT_X = 8       # 左图X起点
    ANCHOR_RIGHT_X = 517    # 右图X起点
    ANCHOR_Y = 190          # Y起点
    CLIP_WIDTH = 10
    CLIP_HEIGHT = 10
    DIFF_LIMIT = 2000       # 差异阀值，两片图形对比差异差异超过此值视为不一样


class MeinvConfig(WindowConfig):
    WIDTH = 498             # 图宽
    HEIGHT = 448            # 图高
    ANCHOR_LEFT_X = 8       # 左图X起点
    ANCHOR_RIGHT_X = 517    # 右图X起点
    ANCHOR_Y = 190          # Y起点


class DajiaConfig(WindowConfig):
    WIDTH = 381
    HEIGHT = 286
    ANCHOR_LEFT_X = 10
    ANCHOR_RIGHT_X = 403
    ANCHOR_Y = 184


class WindowWrap(object):
    def __init__(self, hwnd):
        self.hwnd = long(hwnd)

    def width(self):
        return self.rect().width()

    def height(self):
        return self.rect().height()

    def size(self):
        return self.rect().size()

    def winid(self):
        return self.hwnd

    def rect(self):
        r = win32gui.GetWindowRect(self.hwnd)
        return QtCore.QRect(r[0], r[1], r[2] - r[0], r[3] - r[1])

    def pos(self):
        return self.rect().topLeft()


class GameWnd(WindowWrap):
    target = 0

    def __init__(self, hwnd, target):
        super(GameWnd, self).__init__(hwnd)
        self.target = target

    @property
    def config(self):
        if self.width() == 1024 and self.height() == 738:
            return MeinvConfig
        elif self.width() == 800 and self.height() == 600:
            return DajiaConfig
        else:
            log("Bad window size!")
            return DajiaConfig

    def left_img_rect(self):
        r = self.rect()
        return QtCore.QRect(
            r.x() + self.config.ANCHOR_LEFT_X,
            r.y() + self.config.ANCHOR_Y,
            self.config.WIDTH,
            self.config.HEIGHT)

    def right_img_rect(self):
        r = self.rect()
        return QtCore.QRect(
            r.x() + self.config.ANCHOR_RIGHT_X,
            r.y() + self.config.ANCHOR_Y,
            self.config.WIDTH,
            self.config.HEIGHT)

    def target_rect(self):
        if self.target:
            return self.right_img_rect()
        else:
            return self.left_img_rect()

    def show_rect(self):
        if self.target:
            return self.left_img_rect()
        else:
            return self.right_img_rect()


class Assist(object):
    GAME_CLASS = "#32770"
    GAME_TITLE = u"大家来找茬"
    INTERVAL = 200
    target = 0

    def __init__(self):
        self.img = None
        self.cfg_panel = ConfigPanel()
        self.cfg_panel.start_clicked.connect(self.onStart)
        self.cover_panel = CoverPanel()
        self.game_wnd = None
        t = QtCore.QTimer()
        t.setInterval(self.INTERVAL)
        t.timeout.connect(self.grab_game_iamge)
        self.timer = t
        self.cfg_panel.setInterval(self.INTERVAL)
        self.cfg_panel.interval_changed.connect(self.set_timer_interval)

    def set_timer_interval(self, val):
        self.timer.setInterval(val)

    def show(self):
        self.cfg_panel.show()

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()
        self.cover_panel.showImage(None)

    def onStart(self):
        if self.timer.isActive():
            self.stop()
        else:
            self.timer.start()

    def get_game_window(self):
        hwnd = win32gui.FindWindow(self.GAME_CLASS,
                                   self.GAME_TITLE.encode("gbk"))

        return hwnd and GameWnd(hwnd, self.target) or None

    def relocate_panel(self):
        game_wnd = self.get_game_window()
        if game_wnd is None:
            log('Game window not found!')
            self.reset()
            return
        self.game_wnd = game_wnd
        self.cover_panel.setGeometry(game_wnd.show_rect())

    def reset(self):
        pass

    def snap(self, fmt="qt"):
        def check_swicth(gw):
            cur_pos = QtGui.QCursor.pos()
            rect = gw.show_rect()
            if rect.contains(cur_pos.x(), cur_pos.y()):
                self.target = not self.target

        gw = self.get_game_window()
        if gw:
            check_swicth(gw)
            r = gw.target_rect()
            if fmt == 'qt':
                return QtGui.QPixmap.grabWindow(
                    QtGui.QApplication.desktop().winId(),
                    r.x(), r.y(), r.width(), r.height())
            else:
                return ImageGrab.grab((r.x(), r.y(), r.right(), r.bottom()))

    def grab_game_iamge(self):
        self.relocate_panel()
        img = self.snap()
        if img != self.img:
            self.cover_panel.showImage(self.img)
            self.img = img
        else:
            self.stop()
        self.cover_panel.toggle()


class CoverPanel(QtGui.QWidget):
    def __init__(self):
        super(CoverPanel, self).__init__(None)
        Qt = QtCore.Qt
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.WindowStaysOnTopHint
                            | Qt.Popup
                            | Qt.Tool)
        self.img = None

    def toggle(self):
        if self.isVisible():
            self.hide()
        elif self.img:
            self.show()

    def showImage(self, pImage):
        self.img = pImage
        if pImage is None:
            self.toggle()
        self.repaint()

    def paintEvent(self, e):
        if self.img:
            painter = QtGui.QPainter(self)
            painter.drawPixmap(self.rect(), self.img)


class ConfigPanel(QtGui.QWidget):
    start_clicked = QtCore.Signal()
    interval_changed = QtCore.Signal(int)

    def __init__(self):
        super(ConfigPanel, self).__init__(None)
        self.setWindowTitle(u'找茬助手')
        lo = QtGui.QVBoxLayout()
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMaximum(1000)
        self.slider.setMinimum(50)
        self.slider.setSingleStep(50)
        self.slider.valueChanged.connect(self.interval_changed)
        lo.addWidget(self.slider)
        self.btn_start = QtGui.QPushButton()
        self.btn_start.setText(u'开关')
        self.btn_start.clicked.connect(self.onStartClicked)
        lo.addWidget(self.btn_start)
        self.setLayout(lo)

    def setInterval(self, v):
        self.slider.setValue(v)

    def onStartClicked(self):
        self.start_clicked.emit()


def main():
    app = QtGui.QApplication([])
    assist = Assist()
    assist.show()
    app.exec_()


if __name__ == '__main__':
    main()

# USB camera display using PyQt and OpenCV, from iosoft.blog
# Copyright (c) Jeremy P Bentham 2019
# Please credit iosoft.blog if you use the information or software in it

VERSION = "Cam_display v0.10"

import sys, time, threading, cv2, argparse, os
try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QPushButton
    from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout, QGridLayout, QSlider
    from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor, QPixmap
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt4.QtGui import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QPainter, QImage, QTextCursor

# Main window
class MyWindow(QMainWindow):
    text_update = pyqtSignal(str)

    # Create main window
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.central = QWidget(self)

        self.shoot = QPushButton("Take picture")
        self.shoot.clicked.connect(lambda:self.savePicture())


        self.share = QPushButton("Share")
        self.share.clicked.connect(lambda:self.sharePicture())

        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.shoot)
        self.buttons.addWidget(self.share)

        # Emotion controls
        self.sliders = []
        self.values = []
        self.controls = QGridLayout()
        self.controls.addLayout(self.buttons, 0, 0, 1, 3)
        self.controls.addLayout(self.addSlider("Happiness"), 1, 0);
        self.controls.addLayout(self.addSlider("Sadness"), 1, 1);
        self.controls.addLayout(self.addSlider("Fear"), 1, 2);
        self.controls.addLayout(self.addSlider("Disgust"), 2, 0);
        self.controls.addLayout(self.addSlider("Anger"), 2, 1);
        self.controls.addLayout(self.addSlider("Surprise"), 2, 2);

        self.sliders[0].setValue(50)

        self.central.setLayout(self.controls)
        self.setCentralWidget(self.central)

        self.setFixedWidth(800)
        self.setFixedHeight(150)
        self.move(0,330)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def addSlider(self, text):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(20)
        slider.setFont(QFont('Arial', 8))
        slider.valueChanged.connect(self.valueChanged)
        self.sliders.append(slider)
        self.values.append(0)

        label = QLabel(text)
        label.setFont(QFont('Arial', 8))
        label.setMargin(0)

        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)
        vlayout.addWidget(label)
        vlayout.addWidget(slider)
        return vlayout

    def savePicture(self):
        os.system("touch ./shoot")

    def sharePicture(self):
        os.system("touch ./share")

    def valueChanged(self):
        for key  in range(0, len(self.sliders)):
            self.values[key] = str(self.sliders[key].value())

        f = open("values.txt", "wt")
        f.write(";".join(self.values))
        f.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    win.showMaximized()
    win.setWindowTitle(VERSION)
    sys.exit(app.exec_())

#EOF

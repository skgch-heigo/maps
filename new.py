import random
import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
import finder
import window

# toponym_to_find = " ".join(sys.argv[1:])
#
# coords = tuple(finder.get_coords(toponym_to_find))
#
# orgs = finder.get_org("Аптека", coords, 10)
#
## inf = {"Расстояние": finder.lonlat_distance(coords, tuple(map(float, org[2].split(",")))),
##        "Адрес": org[1], "Название": org[0], "Время работы": org[3]["Hours"]["text"]}
#
# ans = [1000, -1000, 1000, -1000]
# points = []
# for i in orgs:
#    ans[0] = min(ans[0], float(i[2].split(",")[0]))
#    ans[1] = max(ans[1], float(i[2].split(",")[0]))
#    ans[2] = min(ans[2], float(i[2].split(",")[1]))
#    ans[3] = max(ans[3], float(i[2].split(",")[1]))
#    color = "pm2bll"
#    if "Hours" not in i[3]:
#        color = "pm2grl"
#    elif "круглосуточно" in i[3]["Hours"]["text"]:
#        color = "pm2gnl"
#    points.append((i[2], color))
#
## ll_span = finder.get_ll_span(org[1])
#
# response = finder.get_map(",".join([str((ans[0] + ans[1]) / 2), str((ans[2] + ans[3]) / 2)]),
#                          ",".join([str((ans[1] - ans[0])), str((ans[3] - ans[2]))]),
#                          points)
#
# map_file = "map.png"
# with open(map_file, "wb") as file:
#    file.write(response.content)

# Инициализируем pygame
SCREEN_SIZE = [650, 450]


class Example(QMainWindow, window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.tp = "map"
        self.pm = None
        self.post = False
        self.postal = ""
        self.setupUi(self)
        self.getImage()
        self.initUI()

    def getImage(self):
        response = finder.get_map(str(self.doubleSpinBox.value()) + "," + str(self.doubleSpinBox_2.value()),
                                  str(self.horizontalSlider.value() / 1000) + "," +
                                  str(self.horizontalSlider.value() / 1000), tp=self.tp, points=self.pm)
        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.label.setPixmap(QPixmap.fromImage(self.img))
        if not self.hasFocus():
            self.setFocus()

    def initUI(self):
        self.radioButton.clicked.connect(self.change_tp)
        self.radioButton_2.clicked.connect(self.change_tp)
        self.radioButton_3.clicked.connect(self.change_tp)
        self.radioButton_4.clicked.connect(self.change_tp)
        self.doubleSpinBox.valueChanged.connect(self.getImage)
        self.doubleSpinBox_2.valueChanged.connect(self.getImage)
        self.horizontalSlider.valueChanged.connect(self.getImage)
        self.label.setPixmap(QPixmap.fromImage(self.img))
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.clr)
        self.checkBox.clicked.connect(self.post_ind)

    def post_ind(self):
        if self.checkBox.isChecked():
            self.post = True
            if self.lineEdit_2.text():
                self.postal = finder.get_postal_code(self.lineEdit_2.text())
                self.lineEdit_2.setText(self.lineEdit_2.text() + ", " + self.postal)
        else:
            if self.lineEdit_2.text():
                self.lineEdit_2.setText(self.lineEdit_2.text()[:len(self.lineEdit_2.text()) - len(self.postal) - 2])
            self.postal = ""
            self.post = False

    def run(self):
        if self.lineEdit.text():
            addr = finder.get_full_addr(self.lineEdit.text())
            self.lineEdit_2.setText(addr)
            if self.post:
                self.postal = finder.get_postal_code(self.lineEdit_2.text())
                self.lineEdit_2.setText(self.lineEdit_2.text() + ", " + self.postal)
            ll, span = finder.get_ll_span(self.lineEdit.text())
            coords = tuple(map(float, ll.split(",")))
            span = tuple(map(float, span.split(",")))
            max_sp = max(span)
            self.horizontalSlider.setValue(int(max(min(max_sp * 1000, 500), 1)))
            self.pm = [(ll, "pm2bll")]
            self.doubleSpinBox.setValue(coords[0])
            self.doubleSpinBox_2.setValue(coords[1])
            self.getImage()

    def clr(self):
        self.pm = None
        self.lineEdit_2.setText("")
        self.postal = ""
        self.getImage()

    def change_tp(self):
        if self.radioButton.isChecked():
            self.tp = "map"
        elif self.radioButton_2.isChecked():
            self.tp = "sat"
        elif self.radioButton_3.isChecked():
            self.tp = "sat,skl"
        elif self.radioButton_4.isChecked():
            self.tp = "map,trf,skl"
        self.getImage()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.horizontalSlider.setValue(min(500, self.horizontalSlider.value() + 5))
            self.getImage()
        if event.key() == Qt.Key_PageDown:
            self.horizontalSlider.setValue(max(1, self.horizontalSlider.value() - 5))
            self.getImage()
        if event.key() == Qt.Key_Down:
            self.doubleSpinBox_2.setValue(max(-90, self.doubleSpinBox_2.value() - self.horizontalSlider.value() / 2000))
            self.getImage()
        if event.key() == Qt.Key_Up:
            self.doubleSpinBox_2.setValue(min(90, self.doubleSpinBox_2.value() + self.horizontalSlider.value() / 2000))
            self.getImage()
        if event.key() == Qt.Key_Right:
            self.doubleSpinBox.setValue(min(180, self.doubleSpinBox.value() + self.horizontalSlider.value() / 1000))
            self.getImage()
        if event.key() == Qt.Key_Left:
            self.doubleSpinBox.setValue(max(-180, self.doubleSpinBox.value() - self.horizontalSlider.value() / 1000))
            self.getImage()

    def mousePressEvent(self, event):
        left_x = ((self.label.x() + self.label.width()) // 2 - SCREEN_SIZE[0] // 2)
        left_y = ((self.label.y() + self.label.height()) // 2 - SCREEN_SIZE[1] // 2)
        if left_x < event.x() < SCREEN_SIZE[0] + left_x and \
                left_y < event.y() < SCREEN_SIZE[1] + left_y:
            x = (event.x() - SCREEN_SIZE[0] // 2 - left_x) / SCREEN_SIZE[0] \
                * (self.horizontalSlider.value() / 1000) / 450 * 650
            y = (event.y() - SCREEN_SIZE[1] // 2 - left_y) / SCREEN_SIZE[1] \
                * (self.horizontalSlider.value() / 1000)
            if event.button() == Qt.LeftButton:
                addr = finder.get_full_addr(str(self.doubleSpinBox.value() + x) + "," +
                                            str(self.doubleSpinBox_2.value() - y))
                self.lineEdit_2.setText(addr)
                if self.post:
                    self.postal = finder.get_postal_code(str(self.doubleSpinBox.value() + x) + "," +
                                                         str(self.doubleSpinBox_2.value() - y))
                    self.lineEdit_2.setText(
                        self.lineEdit_2.text() + ", " + self.postal)
                self.pm = [(str(self.doubleSpinBox.value() + x) + "," +
                            str(self.doubleSpinBox_2.value() - y), "pm2bll")]
                self.getImage()
            elif event.button() == Qt.RightButton:
                pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

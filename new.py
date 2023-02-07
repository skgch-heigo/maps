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


#toponym_to_find = " ".join(sys.argv[1:])
#
#coords = tuple(finder.get_coords(toponym_to_find))
#
#orgs = finder.get_org("Аптека", coords, 10)
#
## inf = {"Расстояние": finder.lonlat_distance(coords, tuple(map(float, org[2].split(",")))),
##        "Адрес": org[1], "Название": org[0], "Время работы": org[3]["Hours"]["text"]}
#
#ans = [1000, -1000, 1000, -1000]
#points = []
#for i in orgs:
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
#response = finder.get_map(",".join([str((ans[0] + ans[1]) / 2), str((ans[2] + ans[3]) / 2)]),
#                          ",".join([str((ans[1] - ans[0])), str((ans[3] - ans[2]))]),
#                          points)
#
#map_file = "map.png"
#with open(map_file, "wb") as file:
#    file.write(response.content)

# Инициализируем pygame
SCREEN_SIZE = [600, 450]


class Example(QMainWindow, window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.getImage()
        self.initUI()

    def getImage(self):
        response = finder.get_map(str(self.doubleSpinBox.value()) + "," + str(self.doubleSpinBox_2.value()),
                                  str(self.horizontalSlider.value() / 100) + "," +
                                  str(self.horizontalSlider.value() / 100))
        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.label.setPixmap(QPixmap.fromImage(self.img))

    def initUI(self):
        self.doubleSpinBox.valueChanged.connect(self.getImage)
        self.doubleSpinBox_2.valueChanged.connect(self.getImage)
        self.horizontalSlider.valueChanged.connect(self.getImage)
        self.label.setPixmap(QPixmap.fromImage(self.img))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.horizontalSlider.value = min(99, self.horizontalSlider.value + 10)
            self.getImage()
        if event.key() == Qt.Key_PageDown:
            self.horizontalSlider.value = max(1, self.horizontalSlider.value - 10)
            self.getImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())

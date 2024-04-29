import csv
import sys
from typing import List,Optional

from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import QCommandLineParser
from PySide2.QtGui import QPainter

import uiloader
import maps
from locator import Locator

from zoom import QtImageViewer

cols = [(0, 255, 0), (255, 255, 0), (0, 255, 255)]


# GPS:archfalhwyl #1:1070609.55:121701.79:1583667.99:#FF75C9F1:
def XYZtoGPS(x, y, z):
    return "GPS:aaa:{0:.2f}:{1:.2f}:{2:.2f}:#FF75C9F1".format(x, y, z)


class Point:
    def __init__(self, lat, lon, r, g, b, txt):
        self.lat = lat
        self.lon = lon
        self.r = r
        self.g = g
        self.b = b
        self.txt = txt

    def qtcolor(self) -> QtGui.QColor:
        return QtGui.QColor(self.r, self.g, self.b)

    def writeRow(self, csvwriter):
        csvwriter.writerow((self.lat, self.lon, self.r, self.g, self.b, self.txt))

    @staticmethod
    def readRow(row):
        return Point(float(row[0]), float(row[1]), int(row[2]), int(row[3]), int(row[4]), row[5])

    def __str__(self):
        return "Point({0},{1},{2},{3},{4},{5})".format(self.lat, self.lon, self.r, self.g, self.b, self.txt)


class UI(QtWidgets.QMainWindow):
    points: List[Point]
    loc: Locator
    origmap: QtGui.QPixmap
    imgview: QtImageViewer
    selected: Optional[int]

    def __init__(self, planet):
        super().__init__()
        uiloader.loadUi('main.ui', self)
        csv.register_dialect("custom", delimiter=":", skipinitialspace=True)
        try:
            self.loc = maps.data[planet]
        except KeyError:
            raise Exception(f"Cannot find planet data {planet}")

        self.imgview.loadImageFromFile(self.loc.mapfile)
        self.origmap = QtGui.QPixmap(self.imgview.pixmap())
        self.show()
        self.goButton.clicked.connect(self.newptcoords)
        self.stringButton.clicked.connect(self.newptstring)
        self.clearButton.clicked.connect(self.clear)
        self.writeButton.clicked.connect(self.save)
        self.xyzButton.clicked.connect(self.latLonToXYZ)
        self.imgview.midMouseButtonPressed.connect(self.midButtonPressed)
        self.imgview.imageUpdated.connect(self.imageUpdated)

        self.recursingImageUpdated = False
        self.clear()
        self.load()
        self.selected = None

    def save(self):
        with open(self.loc.datafile, 'w', newline='') as f:
            writer = csv.writer(f, dialect="custom")
            for p in self.points:
                p.writeRow(writer)

    def load(self):
        try:
            with open(self.loc.datafile) as f:
                reader = csv.reader(f, dialect='custom')
                for row in reader:
                    self.points.append(Point.readRow(row))
        except FileNotFoundError:
            pass

    def clear(self):
        self.points = []
        self.selected = None

    def cross(self, painter: QPainter, zoom: float, point: Point, selected: bool):
        x, y = self.loc.screenpos(point.lat, point.lon)
        pen = QtGui.QPen(point.qtcolor())
        w = max(1.0, 20.0 / zoom)
        print("zoom", zoom, "width", w)
        pen.setWidthF(w)
        painter.setPen(pen)
        crossSize = 40 / zoom
        if selected:
            crossSize = crossSize * 2
            painter.drawEllipse(int(x - crossSize), int(y - crossSize), int(crossSize * 2), int(crossSize * 2))
        painter.drawLine(int(x - crossSize), int(y - crossSize), int(x + crossSize), int(y + crossSize))
        painter.drawLine(int(x + crossSize), int(y - crossSize), int(x - crossSize), int(y + crossSize))
        painter.drawText(int(x + 40 / zoom), int(y), point.txt)

    def imageUpdated(self):
        if self.recursingImageUpdated:
            return
        # we have to make a copy of the pixmap and store it in a local because QPainter will not store a reference
        # to it, resulting in it being garbage collected and a crash occurring.
        tmp = QtGui.QPixmap(self.origmap)
        p = QtGui.QPainter(tmp)
        f = QtGui.QFont()
        zoom = self.imgview.zoomFactor
        fontsize = max(10, 200 / zoom)
        f.setPixelSize(int(fontsize))
        p.setFont(f)
        self.recursingImageUpdated = True
        self.imgview.setImage(self.origmap)
        for i, point in enumerate(self.points):
            self.cross(p, zoom, point, i == self.selected)
        p.end()
        self.imgview.setImage(tmp)
        self.recursingImageUpdated = False

    def addPoint(self, lat, lon, txt):
        r, g, b = cols[len(self.points) % len(cols)]
        self.points.append(Point(lat, lon, r, g, b, txt))
        self.imageUpdated()

    # GPS:archfalhwyl #1:1070609.55:121701.79:1583667.99:#FF75C9F1:
    def newptstring(self):
        try:
            s = self.string.text().split(':')
            x = float(s[2])
            y = float(s[3])
            z = float(s[4])
            print("WOB")
            lat, lon = self.loc.coords(x, y, z)
            self.latOut.setText(str(lat))
            self.lonOut.setText(str(lon))
            self.addPoint(lat, lon, "GPS" + str(len(self.points)))
            print(lat, lon)

        except ValueError as e:
            raise e

    def newptcoords(self):
        try:
            x = float(self.xedit.text())
            y = float(self.yedit.text())
            z = float(self.zedit.text())
            lat, lon = self.loc.coords(x, y, z)
            self.addPoint(lat, lon, "XYZ" + str(len(self.points)))
            print(lat, lon)
        except ValueError as e:
            raise e

    def gotoLatLon(self, lat, lon):
        self.latOut.setText(str(lat))
        self.lonOut.setText(str(lon))
        x, y, z = self.loc.XYZfromLatLon(lat, lon)
        self.addPoint(lat, lon, "MAP" + str(len(self.points)))
        self.xedit.setText(str(x))
        self.yedit.setText(str(y))
        self.zedit.setText(str(z))
        self.string.setText(XYZtoGPS(x, y, z))

    def midButtonPressed(self, x, y):
        lat, lon = self.loc.latLonFromScreen(x, y)
        self.gotoLatLon(lat, lon)

    def latLonToXYZ(self):
        lat = float(self.latOut.text())
        lon = float(self.lonOut.text())
        self.gotoLatLon(lat, lon)


def main():
    app = QtWidgets.QApplication(sys.argv)
    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("planet", "mars/earth/earthores")

    parser.process(app)
    args = parser.positionalArguments()

    planet = "earth"
    if len(args) > 0:
        planet = args[0]

    window = UI(planet)
    app.exec_()


if __name__ == "__main__":
    main()

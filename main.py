from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt,QCommandLineOption,QCommandLineParser
import sys,math,csv

cols = [(0,255,0),(255,255,0),(0,255,255)]

class Locator:
    def __init__(self):
        pass
 

    def coords(self,x,y,z):
        xr = x-self.X
        yr = y-self.Y
        zr = z-self.Z

        mag = math.sqrt(xr*xr+yr*yr+zr*zr)
        xr = xr/mag
        yr = yr/mag
        zr = zr/mag

        print(x,y,z)

        print(xr,yr,zr)
        lat=math.asin(yr)
        lon=math.atan2(xr,zr)
        return (math.degrees(lat),math.degrees(lon))

    def XYZfromLatLon(self,lat,lon):
        theta = math.radians(lon)
        xr = self.K * math.sin(theta)
        zr = self.K * math.cos(theta)
        print("DECODING ",lat)
        yr = self.K * math.sin(math.radians(lat))
        x = xr+self.X
        y = yr+self.Y
        z = zr+self.Z
        return x,y,z
        
    def screenpos(self,lat,lon):    
        while lat<-90:
            lat = lat+90
        while lat>90:
            lat = lat-90
            
        while lon<0:
            lon = lon+360
        while lon>360:
            lon = lon-360
            
        lon = lon/360.0
        lat = (lat+90)/180.0
        x = self.lon0x+(self.lon360x-self.lon0x)*lon
        y = self.latminus90y+(self.lat90y-self.latminus90y)*lat
        print(x,y)
        return x,y
    
    def latLonFromScreen(self,x,y):
        x = (x-self.lon0x)/(self.lon360x-self.lon0x)
        y = (y-self.latminus90y)/(self.lat90y-self.latminus90y)
        lat = y*180.0-90.0
        lon = x*360.0
        print("LAT,LON",lat,lon)
        return lat,lon

# GPS:archfalhwyl #1:1070609.55:121701.79:1583667.99:#FF75C9F1:
def XYZtoGPS(x,y,z):
    return "GPS:aaa:{0:.2f}:{1:.2f}:{2:.2f}:#FF75C9F1".format(x,y,z)

    
class MarsLocator(Locator):
    def __init__(self):
        super().__init__()
        self.X = 1031072.5
        self.Y = 131072.5
        self.Z = 1631072.5
        self.K = 63292 # radius
        self.lat90y=327
        self.latminus90y=4421
        self.lon0x=257
        self.lon360x=8448
        self.mapfile = "mars.png"
        self.datafile = "marsdata"

class EarthLocator(Locator):
    def __init__(self):
        super().__init__()
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.K = 60000 # radius
        self.lat90y=0
        self.latminus90y=4095
        self.lon0x=0
        self.lon360x=8191
        self.mapfile = "earth.png"
        self.datafile = "earthdata"

class EarthOresLocator(Locator):
    def __init__(self):
        super().__init__()
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.K = 60000 # radius
        self.lat90y=327
        self.latminus90y=4421
        self.lon0x=257
        self.lon360x=8448
        self.mapfile = "earthores.png"
        self.datafile = "earthdata"
    
class UI(QtWidgets.QMainWindow):
    def __init__(self,planet):
        super().__init__()
        uic.loadUi('main.ui',self)
        csv.register_dialect("custom", delimiter=":", skipinitialspace=True)
        if planet=='mars':
            self.loc = MarsLocator()
        elif planet=='earthores':
            self.loc = EarthOresLocator()
        else:
            self.loc = EarthLocator()
         
        self.imgview.loadImageFromFile(self.loc.mapfile)
        self.origmap = QtGui.QPixmap(self.imgview.pixmap())
        self.show()
        self.goButton.clicked.connect(self.newptcoords)
        self.stringButton.clicked.connect(self.newptstring)
        self.clearButton.clicked.connect(self.clear)
        self.writeButton.clicked.connect(self.save)
        self.imgview.midButtonHook = self
        self.recursingImageUpdated=False
        self.imgview.imageUpdateHook = self
        self.clear()
        self.load()
        self.curnum=len(self.points)-1

    def save(self):
        with open(self.loc.datafile,'w',newline='') as f:
            writer = csv.writer(f, dialect="custom")
            for p in self.points:
                writer.writerow(p)

    def load(self):
        try:
            with open(self.loc.datafile) as f:
                reader = csv.reader(f,dialect='custom')
                for row in reader:
                    p = (float(row[0]),float(row[1]),int(row[2]),int(row[3]),int(row[4]),row[5])
                    self.points.append(p)
        except FileNotFoundError:
            pass                

    def clear(self):
        self.points = []
        
    def cross(self,p,lat,lon,zoom,txt,r,g,b):
        x,y = self.loc.screenpos(lat,lon)
        pen = QtGui.QPen(QtGui.QColor(r,g,b))
        w = max(1,20/zoom)
        print("zoom",zoom,"width",w)
        pen.setWidthF(w)
        p.setPen(pen)
        crossSize=40/zoom
        p.drawLine(x-crossSize,y-crossSize,x+crossSize,y+crossSize)
        p.drawLine(x+crossSize,y-crossSize,x-crossSize,y+crossSize)
        p.drawText(x+40/zoom,y,txt)

    def imageUpdated(self):
        if self.recursingImageUpdated:
            return
        map = QtGui.QPixmap(self.origmap) # copy
        p = QtGui.QPainter(map)
        f = QtGui.QFont()
        zoom = self.imgview.zoomFactor
        f.setPixelSize(max(10,200/zoom))
        p.setFont(f)
        self.recursingImageUpdated=True
        self.imgview.setImage(self.origmap)
        for lat,lon,r,g,b,txt in self.points:
            self.cross(p,lat,lon,zoom,txt,r,g,b)
        p.end()
        self.imgview.setImage(map)
        self.recursingImageUpdated=False

    def addPoint(self,lat,lon,txt):
        r,g,b = cols[self.curnum%len(cols)]
        self.curnum=self.curnum+1
        pt = (lat,lon,r,g,b,txt)
        self.points.append(pt)
        self.imageUpdated()
        

        
    # GPS:archfalhwyl #1:1070609.55:121701.79:1583667.99:#FF75C9F1:
    def newptstring(self):
        try:
            s = self.string.text().split(':')
            x = float(s[2])
            y = float(s[3])
            z = float(s[4])
            print("WOB")
            lat,lon = self.loc.coords(x,y,z)
            self.latOut.setText(str(lat))
            self.lonOut.setText(str(lon))
            self.addPoint(lat,lon,"GPS"+str(self.curnum))
            print(lat,lon)

        except ValueError as e:
            raise e

    def newptcoords(self):
        try:
            x = float(self.xedit.text())
            y = float(self.yedit.text())
            z = float(self.zedit.text())
            lat,lon = self.loc.coords(x,y,z)
            self.addPoint(lat,lon,"XYZ"+str(self.curnum))
            print(lat,lon)
        except ValueError as e:
            raise e

    def midButtonPressed(self,x,y):
        lat,lon = self.loc.latLonFromScreen(x,y)
        self.latOut.setText(str(lat))
        self.lonOut.setText(str(lon))
        x,y,z = self.loc.XYZfromLatLon(lat,lon)
        self.addPoint(lat,lon,"MAP"+str(self.curnum))
        self.xedit.setText(str(x))
        self.yedit.setText(str(y))
        self.zedit.setText(str(z))
        self.string.setText(XYZtoGPS(x,y,z))

    def midButtonReleased(self,x,y):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("planet", "mars/earth/earthores")

    parser.process(app)
    args = parser.positionalArguments() 

    planet = "earth"
    if len(args)>0:
        planet = args[0]
        
    window = UI(planet)
    app.exec_()
    
if __name__ == "__main__":
    main()

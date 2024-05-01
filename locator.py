import math


class Locator:
    def __init__(self, mapfile, datafile, cx, cy, cz, radius,
                 lat90y=0, latminus90y=4095, lon0x=0, lon360x=8191, lonOffset=0, flipv=True, fliph=True):

        self.mapfile = mapfile
        self.datafile = datafile
        self.X = cx
        self.Y = cy
        self.Z = cz
        self.K = radius
        self.lat90y = lat90y
        self.latminus90y = latminus90y
        self.lon0x = lon0x
        self.lon360x = lon360x
        self.lonOffset = lonOffset      # this is the longitude at the left edge of the map, which is normally 0
        self.flipv = flipv              # true if the map is flipped vertically
        self.fliph = fliph              # true if the map is flipped horizontally

    def latLonFromXYZ(self, x, y, z):
        xr = x - self.X
        yr = y - self.Y
        zr = z - self.Z

        mag = math.sqrt(xr * xr + yr * yr + zr * zr)
        xr = xr / mag
        yr = yr / mag
        zr = zr / mag

        print(f"Difference from planetary radius: {mag-self.K}")

        print(x, y, z)

        print(xr, yr, zr)
        lat = math.degrees(math.asin(yr))
        lon = math.degrees(math.atan2(xr, zr))
        return lat, lon

    def XYZfromLatLon(self, lat, lon):
        theta = math.radians(lon)
        xr = self.K * math.sin(theta)
        zr = self.K * math.cos(theta)
        print("DECODING ", lat)
        yr = self.K * math.sin(math.radians(lat))
        x = xr + self.X
        y = yr + self.Y
        z = zr + self.Z
        return x, y, z

    def screenFromLatLon(self, lat, lon):
        while lat < -90:
            lat = lat + 90
        while lat > 90:
            lat = lat - 90

        lon = ((lon+360) - self.lonOffset) % 360

        while lon < 0:
            lon = lon + 360
        while lon > 360:
            lon = lon - 360

        lon = lon / 360.0
        lat = (lat + 90) / 180.0
        x = self.lon0x + (self.lon360x - self.lon0x) * lon
        y = self.latminus90y + (self.lat90y - self.latminus90y) * lat
        print(x, y)
        return x, y

    def latLonFromScreen(self, x, y):
        x = (x - self.lon0x) / (self.lon360x - self.lon0x)
        y = (y - self.latminus90y) / (self.lat90y - self.latminus90y)
        lat = y * 180.0 - 90.0
        lon = x * 360.0
        lon = (lon + 360 + self.lonOffset) % 360

        print("LAT,LON", lat, lon)
        return lat, lon

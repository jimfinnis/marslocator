from locator import Locator

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
        self.mapfile = "maps/mars.png"
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
        self.mapfile = "maps/earth.png"
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
        self.mapfile = "maps/earthores.png"
        self.datafile = "earthdata"

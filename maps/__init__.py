from locator import Locator


mars = Locator("maps/mars.png","marsdata",
    1031072.5, 131072.5, 63292,
    327, 4421, 257, 8448)

earth = Locator("maps/earth.png","earthdata",
    0,0,0,60000)
    
earthores = Locator("maps/earthores.png","earthdata",
    0,0,0,60000,
    327, 4421, 257, 8448)


data = {"mars": mars,
         "earth": earth,
         "earthores": earthores
       }

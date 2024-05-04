from locator import Locator

# |MARS;(1032762,134086,1632659);64606;RUST;;;;
# |EUROPA;(916410,16373.72,1616441);9600;LIGHTBLUE;;;;
# |EARTHLIKE;(0,0,0);60000;GREEN;;;;
# |MOON;(16388,136375,-113547);9394;GRAY;;;;
# |TRITON;(-284463.6,-2434464,365536.2);38128.81;WHITE;;;;
# |ALIEN;(131110.8,131220.6,5731113);60894.06;MAGENTA;;;;
# |TITAN;(36385.04,226384,5796385);9238.224;CYAN;;;;

mars = Locator("maps/Mars-auto.png", "maps/Mars-mapdata.json", "marsdata",
               1032762,134086,1632659, 63292)

earth = Locator("maps/Earthlike-auto.png", "maps/Earthlike-mapdata.json", "earthdata",
                0, 0, 0, 60000)

pertam = Locator("maps/Pertam-auto.png", "maps/Pertam-mapdata.json", "pertamdata",
                 -3967232.5, -32232.5, 767232.5, 60000)

titan = Locator("maps/Titan-auto.png", "maps/Titan-mapdata.json", "titandata",
                36384.5, 226384.5, 5796384.5, 9200)

triton = Locator("maps/Triton-auto.png", "maps/Triton-mapdata.json", "tritondata",
                 -284463.5, -2434463.5, 365536.5, 38100)

europa = Locator("maps/Europa-auto.png", "maps/Europa-mapdata.json", "europadata",
                 916384.5, 16384.5, 1616384.5, 9600)

alien = Locator("maps/Alien-auto.png", "maps/Alien-mapdata.json", "aliendata",
                131072.5, 131072.5, 5731072.5, 60900)

moon = Locator("maps/Moon-auto.png", "maps/Moon-mapdata.json", "moondata",
               16384.5, 136384.5, -113615.5, 60000)

# map made in a different system, so no flips.
#earthores = Locator("maps/earthores.png", "maps/Earthlike-mapdata.json", "earthdata",
#                    0, 0, 0, 60000,
#                    327, 4421, 257, 8448)

data = {"mars": mars,
        "earth": earth,
        "pertam": pertam,
        "titan": titan,
        "triton": triton,
        "europa": europa,
        "alien": alien,
        "moon": moon,
        }

import json
import cv2 as cv
import numpy as np

numcontours = 50
thickevery = 10


def imread(x):
    for ext in [".png", ".jpg"]:
        f = cv.imread(x + ext)
        if f is not None:
            return f
    raise FileNotFoundError(x)


def process(planet):
    hmname = f"{planet}-equirect-hm"
    terrname = f"{planet}-equirect"

    print(f"Reading planet {planet}")

    hm = imread(hmname)
    terr = imread(terrname)

    print(f"heightmap: {hm.shape}, terrain: {terr.shape}")

    # convert height map to single channel
    hm = cv.cvtColor(hm, cv.COLOR_BGR2GRAY)
    # find highest and lowest pixel
    maxy,maxx = np.unravel_index(hm.argmax(), hm.shape)
    miny,minx = np.unravel_index(hm.argmin(), hm.shape)

    # multiply by heightmap
    hm2 = hm.astype(np.float32) / 255.0
    hm2 = hm2 ** 0.2
    heightDarkAmount = 0.8
    hm2 = (1.0 - heightDarkAmount) + hm2 * heightDarkAmount
    hm2 = np.dstack([hm2, hm2, hm2])

    terr = terr * hm2
    terr = cv.normalize(terr, terr, 0, 255, cv.NORM_MINMAX)
    print(np.min(terr), np.max(terr))
    

    # determine contour levels
    heights = np.linspace(0, 255, numcontours)
    heights = [int(x) for x in heights[1:-1]]

    # find contours
    for idx, i in enumerate(heights):
        _, thresh = cv.threshold(hm, i, 255, cv.THRESH_BINARY)
        cons, heir = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        showThickContour = ((idx - 1) % thickevery) == 0
        cv.drawContours(terr, cons, -1, (0, 0, 0),
                        2 if showThickContour else 1
                        )

    # flip image around both axes, for reasons to do with the original
    # image format

    # reduces memory
    terr = terr.astype(np.uint8)
    terr = cv.flip(terr, -1)
#    maxy = terr.shape[0]-maxy
#    maxx = terr.shape[1]-maxx
#    miny = terr.shape[0]-miny
#    minx = terr.shape[1]-minx

    cv.imwrite(f"{planet}-auto.png", terr)
    
    
    with open(f"{planet}-mapdata.json","w") as f:
        mapdata = {
            "maxx": int(maxx),
            "maxy": int(maxy),
            "minx": int(minx),
            "miny": int(miny) }
        f.write(json.dumps(mapdata, sort_keys=True, indent=4))


def processall():
    for x in ["Alien", "Earthlike", "Europa", "Mars", "Moon", "Pertam",
              "Titan", "Triton"]:
        process(x)


#processall()
process("Foo")

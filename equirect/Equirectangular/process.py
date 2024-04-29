import cv2 as cv
import numpy as np

numcontours=50
thickevery=10

def imread(x):
    for ext in [".png",".jpg"]:
        f = cv.imread(x+ext)
        if f is not None:
            return f
    raise FileNotFoundError(x)

def process(planet):
    hmname = f"{planet}-equirect-hm"
    terrname = f"{planet}-equirect"
    
    hm = imread(hmname)
    terr = imread(terrname)
    
    print(hm.shape)
    print(terr.shape)
    
    
    # convert height map to single channel
    hm = cv.cvtColor(hm,cv.COLOR_BGR2GRAY)
    
    heights = np.linspace(0,255,numcontours)
    heights = [int(x) for x in heights[1:-1]]
    
    # find contours
    for idx, i in enumerate(heights):
        _, thresh = cv.threshold(hm, i, 255, cv.THRESH_BINARY)
        cons,heir =  cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        print(type(cons))
        showThickContour = ((idx-1)%thickevery)==0
        cv.drawContours(terr, cons, -1, (0,0,0),
            2 if showThickContour else 1
        )
    
    cv.imwrite("foo.png",terr)
        
    

process("Titan")

from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
from cv2 import cv2 as cv
import imutils
import numpy as np

# imports image
img = cv.imread('Crosshairs/c3.png')
# creates canvas to draw contours on
blank = np.zeros(img.shape, dtype='uint8')
# converts image to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# blurs image
blur = cv.GaussianBlur(gray, (1, 1), cv.BORDER_DEFAULT)

# detects canny edges and refines using dilation and erosion
canny = cv.Canny(blur, 100, 200)
dilated = cv.dilate(canny, (1, 1), iterations=1)
eroded = cv.erode(dilated, (1, 1), iterations=1)

# detects contours and draws them onto blank canvas
contours, hierarchies = cv.findContours(
    eroded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
cv.drawContours(blank, contours, -1, (0,255,0), 1)

cnt = contours[0]
x,y,w,h = cv.boundingRect(cnt)
print('Width = ' + str(w))
print('Height = ' + str(h))

rect = cv.minAreaRect(cnt)
box = cv.boxPoints(rect)
box = np.int0(box)

cv.drawContours(blank, [box], -1, (0, 0, 255), 1)
cv.imshow('Contours Drawn', blank)

cv.waitKey(0)

from cv2 import cv2 as cv
import numpy as np

# imports image
img = cv.imread('Crosshairs/c4.png')
# creates canvas to draw contours on
blank = np.zeros(img.shape, dtype='uint8')
# converts image to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('test', gray)
# blurs image
# blur = cv.GaussianBlur(gray, (1, 1), cv.BORDER_DEFAULT)
# detects canny edges and refines using dilation and erosion
canny = cv.Canny(gray, 0, 20)
dilated = cv.dilate(canny, (1, 1), iterations=1)
eroded = cv.erode(dilated, (1, 1), iterations=1)
# detects contours and draws them in green onto blank canvas
contours, hierarchies = cv.findContours(
    canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
cv.drawContours(blank, contours, -1, (0, 255, 0), 1)
cnt = contours[0]
# defines bounding rectangle around crosshair and prints width and height of box
x, y, w, h = cv.boundingRect(cnt)
print('Width = ' + str(w) + ' pixels')
print('Height = ' + str(h) + ' pixels')
# draws bounding box in red onto blank canvas
rect = cv.minAreaRect(cnt)
box = cv.boxPoints(rect)
box = np.int0(box)
cv.drawContours(blank, [box], -1, (0, 0, 255), 1)
cv.imshow('Contours Drawn', blank)

cv.waitKey(0)
cv.destroyAllWindows()

import sys
import os
import math

from google.cloud import automl_v1beta1
from google.cloud import automl
from PIL import Image

from cv2 import cv2 as cv
import numpy as np
import time

# 'content' is base-64-encoded image data.
def get_prediction(content, project_id, model_id):
  prediction_client = automl_v1beta1.PredictionServiceClient()

  name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
  payload = {'image': {'image_bytes': content }}
  params = {}
  request = prediction_client.predict(name=name, payload=payload, params=params)
  return request  # waits till request is returned


def cropImage(uploaded_file):
    '''
    Generate bounding boxes from VisionAPI
    '''
#   os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="D:\lahacksproject\VisionAPIDemo\lahacks.json"
#   file_path = sys.argv[1]
#   project_id = sys.argv[2]
#   model_id = sys.argv[3]

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r'lahacks.json'

    file_path = uploaded_file
    project_id = "fleet-point-308504"
    model_id = "IOD4595987191406002176"

    with open(file_path, 'rb') as ff:
        content = ff.read()

    response = get_prediction(content, project_id, model_id)

    points = []
    for result in response.payload:
        box = result.image_object_detection.bounding_box.normalized_vertices
        for vertice in box:
            points.append([vertice.x, vertice.y])
    
    og_img = cv.imread(file_path)
    height, width, channels = og_img.shape
    cropped_img = og_img[round(height * points[0][1]):round(height * points[1][1]), round(width * points[0][0]):round(width * points[1][0])]
    cv.imwrite('static/img/cropped.png', cropped_img)
    os.remove(uploaded_file)

    time.sleep(1)

    return "img/cropped.png"

def readOutlines(crosshair_file):
    '''
    Reads Outlines with CV
    '''

    # imports image
    img = cv.imread(crosshair_file)
    # creates canvas to draw contours on
    blank = np.zeros(img.shape, dtype='uint8')
    # converts image to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imshow('test', gray)
    # blurs image
    blur = cv.GaussianBlur(gray, (3, 3), cv.BORDER_DEFAULT)
    # detects canny edges and refines using dilation and erosion
    canny = cv.Canny(blur, 0, 20)
    dilated = cv.dilate(canny, (1, 1), iterations=1)
    eroded = cv.erode(dilated, (1, 1), iterations=1)
    # detects contours and draws them in green onto blank canvas
    contours, hierarchies = cv.findContours(
        canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    cv.drawContours(blank, contours, -1, (0, 255, 0), 1)
    cnt = contours[3]
    # defines bounding rectangle around crosshair and prints width and height of box
    x, y, w, h = cv.boundingRect(cnt)
    # print('Width = ' + str(w) + ' pixels')
    # print('Height = ' + str(h) + ' pixels')
    # draws bounding box in red onto blank canvas
    rect = cv.minAreaRect(cnt)
    box = cv.boxPoints(rect)
    box = np.int0(box)
    cv.drawContours(blank, [box], -1, (0, 0, 255), 1)
    cv.imshow('Contours Drawn', blank)
    
    im = Image.open(crosshair_file)
    rgb_im = im.convert('RGB')
    r, g, b = rgb_im.getpixel(((x + math.ceil(w/2)),(y + math.ceil(h/2))))
    thickness = 2 + ((w - 5) * 0.5)
    size = math.floor(h / 2)
    
    #Gap Calculator
    #Finds pixel distance between centers of hairs
    M = cv.moments(contours[0])
    cxR = int(M['m10']/M['m00'])
    cyR = int(M['m01']/M['m00'])
    M = cv.moments(contours[3])
    cxL = int(M['m10']/M['m00'])
    cyL = int(M['m01']/M['m00'])
    dx = cxR - cxL
    dy = cyR - cyL
    D = np.sqrt(dx*dx+dy*dy)
    #Thickness and size roughly increase pixel distance by 2, 2.4 respectively, each addition of gap increases distance by 2
    gap = math.ceil(int(((D - thickness*2 - size*2.4)/2 + (D - thickness*2 - size*2.4)%2)))

    console = "cl_crosshaircolor 5; cl_crosshaircolor_b " + str(b) + "; cl_crosshaircolor_r " + str(r) + "; cl_crosshaircolor_g " + str(g) + "; cl_crosshairsize " + str(size)  + "; cl_crosshairthickness " + str(thickness) + "; cl_crosshairgap " + str(gap)
    cv.destroyAllWindows()

    retData = {
        "red": r,
        "blue": b,
        "green": g,
        "size": size,
        "thickness": thickness,
        "gap": gap,
        "console":console,
    }

    return retData

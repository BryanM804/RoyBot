import pytesseract
import cv2
import re
from PIL import Image

def circle_roy(img):
    imge = Image.open(img)
    data = pytesseract.image_to_boxes(imge)

    dirty_values = data.lower().replace("\n", " ").split(" ")
    values = []
    center = {}

    cv_img = cv2.imread(img)
    h, w, l = cv_img.shape

    thickness = 2
    color = (0, 0, 255) # BGR ?? who tf uses BGR

    roys_found = 0

    # Clear out non alpha characters
    remove = False
    for x in range(len(dirty_values)):
        if x % 6 == 0:
            remove = False

        if x % 6 == 0 and re.search(r"[^(a-z|A-Z|0-9)]", dirty_values[x]) != None:
            remove = True

        if not remove:
            values.append(dirty_values[x])

    for i in range(len(values)):
        # In theory this should never break out of bounds, but it checks anyway just to be safe
        # Sometimes it picks up the 'o' as '0'
        if i + 12 < len(values) and values[i] == "r" and (values[i + 6] == "o" or values[i + 6] == "0") and values[i + 12] == "y":
            center["left"] = int(values[i + 7])
            center["bottom"] = int(values[i + 8])
            center["right"] = int(values[i + 9])
            center["top"] = int(values[i + 10])
            center_point = (int((center["left"] + center["right"]) / 2), h - int((center["top"] + center["bottom"]) / 2))
            radius = (center_point[0] - int(values[i + 1])) + 7
            cv2.circle(cv_img, center_point, radius if radius > 26 else 26, color, thickness)
            #cv2.arrowedLine(cv_img, )
            roys_found += 1
    
    cv2.imwrite(img, cv_img)
    return roys_found
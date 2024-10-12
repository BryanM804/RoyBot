import pytesseract
import cv2
from PIL import Image

#img = "/mnt/2tbdrive/projects/RoyBot/message-imgs/8ec8d56f-7989-4c83-9505-bb6de61fe53c.jpeg"

def circle_roy(img):
    imge = Image.open(img)
    data = pytesseract.image_to_boxes(imge)

    values = data.lower().replace("\n", " ").split(" ")
    center = {}

    cv_img = cv2.imread(img)
    h, w, l = cv_img.shape

    radius = 27
    thickness = 2
    color = (0, 0, 255) # BGR ?? who tf uses BGR

    roys_found = 0

    for i in range(len(values)):
        # In theory this should never break out of bounds, but it checks anyway just to be safe
        if i + 12 < len(values) and values[i] == "r" and values[i + 6] == "o" and values[i + 12] == "y":
            center["left"] = int(values[i + 7])
            center["bottom"] = int(values[i + 8])
            center["right"] = int(values[i + 9])
            center["top"] = int(values[i + 10])
            center_point = (int((center["left"] + center["right"]) / 2), h - int((center["top"] + center["bottom"]) / 2))
            cv2.circle(cv_img, center_point, radius, color, thickness)
            #cv2.arrowedLine(cv_img, )
            roys_found += 1
    
    cv2.imwrite(img, cv_img)
    return roys_found
import pytesseract
import face_recognition
import PIL
import numpy
from PIL import Image
from PIL import ImageSequence
import cv2
import re

TEST_MODE = False

def circle_word(img, word, case_sens=False, success_dest=""):
    success = False
    imge = Image.open(img) if type(img) != PIL.GifImagePlugin.GifImageFile else img
    imge = imge.convert("RGB")
    word = word if case_sens else word.lower()

    cv_img = numpy.array(imge)
    cv_img = cv_img[:, :, ::-1].copy()
    # Tesseract is better at finding text in grayscale images with smooth text
    kernel = numpy.ones((1,1), numpy.uint8)
    gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.dilate(gray_img, kernel, iterations=1)
    gray_img = cv2.erode(gray_img, kernel, iterations=1)

    # data = pytesseract.image_to_boxes(imge).lower().split("\n") if not case_sens else pytesseract.image_to_boxes(imge).split("\n")
    data = pytesseract.image_to_boxes(gray_img).lower().split("\n") if not case_sens else pytesseract.image_to_boxes(gray_img).split("\n")
    data.remove("")

    # Format the data
    double_d = []
    for e in data:
        li = e.split(" ")
        for i in range(len(li)):
            li[i] = int(li[i]) if i > 0 else li[i]
        double_d.append(li)

    if TEST_MODE:
        for letter in double_d:
            print(letter)

    h, w, l = cv_img.shape
    thickness = 2
    color = (0, 0, 255) # BGR ?? who tf uses BGR

    # Clear out non alpha characters

    matching = False
    i = 0
    start_pos = 0
    end_pos = 0
    for l in double_d:
        if re.search(r"[^(a-z|A-Z|0-9)]", l[0]) != None:
            continue
        
        if l[0] == word[i]:
            if i == 0:
                start_pos = l[1]
            i += 1
            matching = True
        else:
            # if TEST_MODE:
                # print(f"{l[0]} does not match {word[i]}")
            matching = False
            i = 0
            # This looks terrible but hear me out
            # If you had a double letter in the beginning of the word it would see the second
            # character doesn't match the second in the word and skip it even though it matches the first letter
            if l[0] == word[i]:
                if i == 0:
                    start_pos = l[1]
                i += 1
                matching = True
        
        if i == len(word) and matching:
            if TEST_MODE:
                print("Circling [proud]")
            end_pos = int(l[3])
            center_point = (int((end_pos + start_pos) / 2), h - int((l[4] + l[2]) / 2))
            r = int(((end_pos - start_pos) / 2) + 10)
            cv2.circle(cv_img, center_point, r, color, thickness)
            success = True
            matching = False
            i = 0
    
    if success and success_dest != "":
        cv2.imwrite(success_dest, cv_img)
    elif success:
        cv2.imwrite(img, cv_img)
    return success

def circle_word_gif(gif_path, word, case_sens=False, success_dest=""):
    gif = Image.open(gif_path)
    for frame in ImageSequence.Iterator(gif):
        if circle_word(frame, word, False, success_dest):
            return True
    return False
            
def circle_face(img):
    
    pass


if TEST_MODE:
    circle_word_gif("/mnt/2tbdrive/projects/RoyBot/attachment-749.gif", "roy", success_dest="/mnt/2tbdrive/projects/RoyBot/circled.png")
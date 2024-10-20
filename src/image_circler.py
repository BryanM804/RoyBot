import pytesseract
from PIL import Image
import cv2
import re

TEST_MODE = False

def circle_word(img, word, case_sens=False):
    imge = Image.open(img)
    word = word if case_sens else word.lower()
    data = pytesseract.image_to_boxes(imge).lower().split("\n") if not case_sens else pytesseract.image_to_boxes(imge).split("\n")
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

    cv_img = cv2.imread(img)
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
            if TEST_MODE:
                print(f"{l[0]} does not match {word[i]}")
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
            matching = False
            i = 0
            
    cv2.imwrite(img, cv_img)
    return

if TEST_MODE:
    circle_word("/mnt/2tbdrive/projects/RoyBot/asdasdasd.png", "roy")
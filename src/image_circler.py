import pytesseract
import face_recognition
import numpy
import random
from PIL import Image
from PIL import ImageSequence
import cv2
import re
import os
from dlib import DLIB_USE_CUDA

TEST_MODE = False

roy_encoding = []

FRAME_HEIGHT = 0.70
FRAME_WIDTH = 0.70
MAX_HEIGHT = 640
MAX_WIDTH = 640

def resize_image(image, is_cvimg=False):
    if is_cvimg:
        h, w, _ = image.shape
    else:
        w, h = image.size
    
    if h > MAX_HEIGHT:
        change_ratio = MAX_HEIGHT / h
        h = MAX_HEIGHT
        w = w * change_ratio
    
    if w > MAX_WIDTH:
        change_ratio = MAX_WIDTH / w
        w = MAX_WIDTH
        h = h * change_ratio

    if is_cvimg:
        return cv2.resize(image, (int(FRAME_WIDTH * w), int(FRAME_HEIGHT * h)))
    else:
        return image.resize((int(FRAME_WIDTH * w), int(FRAME_HEIGHT * h)))


def circle_word(img, word, case_sens=False, overwrite_original=True, gif_frame=False):
    success = False
    imge = Image.open(img) if not gif_frame else img
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
        elif l[0] == word[0]:
            # Catches double letter starts of a word
            # Ex: target_word = roy, rroy would not be caught without this
            start_pos = l[1]
            i = 1
            matching = True
        else:
            # if TEST_MODE:
                # print(f"{l[0]} does not match {word[i]}")
            matching = False
            i = 0
        
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
    
    newloc = img

    if gif_frame:
        cv_img = cv_img[:, :, ::-1].copy()
        return (success, Image.fromarray(cv_img))

    if success:
        if overwrite_original:
            cv2.imwrite(img, cv_img)
        else:
            newloc = "/mnt/2tbdrive/projects/RoyBot/" + str(random.randrange(1, 1000)) + ".png"
            cv2.imwrite(newloc, cv_img)

    return (success, newloc)

def circle_gif(gif_path, word, case_sens=False):
    gif = Image.open(gif_path)
    dur = gif.info.get("duration")
    skip_frames = False
    if gif.n_frames > 200:
        skip_frames = True
        dur *= 2
        # Need duration to be twice as long if you skip every other frame to keep the timing
    contains_roy = False
    frames = []
    i = 1

    for frame in ImageSequence.Iterator(gif):
        if skip_frames and i % 2 == 0:
            i += 1
            continue

        print(f"Processing frame {i} of gif {gif_path[40:]}")
        i += 1

        frame = resize_image(frame, False)
        word_res = circle_word(frame, word, case_sens, gif_frame=True)
        if word_res[0]:
            contains_roy = True
            face_res = circle_face(word_res[1],  gif_frame=True)
            if face_res[0]:
                frames.append(face_res[1])
            else:
                frames.append(word_res[1])
        else:
            face_res = circle_face(frame,  gif_frame=True)
            if face_res[0]:
                contains_roy = True
                frames.append(face_res[1])
            else:
                frames.append(face_res[1])
    if contains_roy:
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=dur , loop=0)
        return (True, gif_path)
    
    return (False, "")
            
def generate_roy_encoding():
    # This takes forever, so the encodings are cached after the first time they get generated
    # Changing the num_jitters will speed it up if necessary
    print(f"CUDA enabled: {DLIB_USE_CUDA}")

    global roy_encoding
    if len(roy_encoding) != 0:
        return
    
    try:
        for roy_face in os.listdir("./roy_imgs"):
            roy_image = face_recognition.load_image_file(f"./roy_imgs/{roy_face}")
            roy_encoding.append(face_recognition.face_encodings(roy_image, num_jitters = 3)[0])
        print("Generated roy face encodings.")
    except Exception as e:
        print(f"Unable to generate encoding: {e}")
    
# Saves image with a random name returned as the second item of a tuple unless overwrite_original = True
# If gif_frame = True returns the Image object of the frame after circling
def circle_face(img_location, overwrite_original=True, gif_frame=False):
    # Check if img_location is valid to avoid errors
    if not gif_frame:
        image = face_recognition.load_image_file(img_location)
    else:
        image = img_location.convert("RGB")
        image = numpy.array(image)

    if len(image) == 0:
        print(f"Face recognition failed to load image at {img_location}") 
        return (False, "")
    
    face_locs = face_recognition.face_locations(image, model="cnn")

    if len(face_locs) == 0:
        if gif_frame:
            return (False, Image.fromarray(image))
        return (False, "")
    else:
        print("Image contains faces")

    if len(roy_encoding) == 0:
        generate_roy_encoding()

    imge = Image.open(img_location) if not gif_frame else img_location
    imge = imge.convert("RGB")
    cv_img = numpy.array(imge)
    cv_img = cv_img[:, :, ::-1].copy()
    
    success = False
    encodings = face_recognition.face_encodings(image, face_locs)
    i = 0
    for face in encodings:
        result = face_recognition.compare_faces(roy_encoding, face, tolerance=0.5)
        if True in result:
            print(result)
            print("Roy located")
            roy_loc = face_locs[i]
            # top, right, bottom, left

            thickness = 12
            color = (0, 0, 255)
            h, _, _ = cv_img.shape
            center_point = (int((roy_loc[1] + roy_loc[3]) / 2), int((roy_loc[2] + roy_loc[0]) / 2))
            r = int(((roy_loc[1] - roy_loc[3]) / 2) + 50)

            if TEST_MODE:
                print(f"Drawing circle at {center_point} with radius {r}, image height: {h}")

            cv2.circle(cv_img, center_point, r, color, thickness)
            success = True
        i += 1
    
    newloc = img_location

    if gif_frame:
        cv_img = cv_img[:, :, ::-1].copy()
        return (success, Image.fromarray(cv_img))

    if success:
        if overwrite_original:
            cv2.imwrite(img_location, cv_img)
        else:
            newloc = "/mnt/2tbdrive/projects/RoyBot/" + str(random.randrange(1, 1000)) + ".png"
            cv2.imwrite(newloc, cv_img)
    
    return (success, newloc)

if TEST_MODE:
    # circle_word_gif("/mnt/2tbdrive/projects/RoyBot/attachment-749.gif", "roy", success_dest="/mnt/2tbdrive/projects/RoyBot/circled.png")
    circle_face("test_image_copy.jpg")
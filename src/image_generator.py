import requests
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains

def generate_message_jpg(message, user, avatar):
    op = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : "/mnt/2tbdrive/projects/RoyBot/message-imgs",
            "browser.helperApps.neverAsk.saveToDisk": "text/csv"}

    op.add_argument("headless")
    op.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=op)

    # First, download avatar image

    img_data = requests.get(avatar).content
    img_path = f"/mnt/2tbdrive/projects/RoyBot/avatars/{user}.png"
    with open(img_path, "wb") as user_avatar:
        # wb for write bytes 4head
        user_avatar.write(img_data)

    # Then go to message generator site and input the info for the message

    driver.get("https://superemotes.com/fake-discord-message-maker")

    name_box = driver.find_element(By.ID, "message-username-1")
    name_box.clear()
    date_box = driver.find_element(By.ID, "message-date-1")
    date_box.clear()
    message_box = driver.find_element(By.ID, "message-body-1")
    message_box.clear()
    avatar_box = driver.find_element(By.ID, "pfp-file-upload-1")
    generate_button = driver.find_element(By.CLASS_NAME, "generate-image-button")
    download_button = driver.find_element(By.CLASS_NAME, "download-image")

    name_box.send_keys(user)
    date_box.send_keys(f"Today at {datetime.now().hour if datetime.now().hour < 13 else datetime.now().hour - 12}:{datetime.now().minute if datetime.now().minute > 9 else "0" + datetime.now().minute} {"AM" if datetime.now().hour < 13 else "PM"}")
    message_box.send_keys(message)
    avatar_box.send_keys(img_path)

    generate_button.click()
    driver.implicitly_wait(2)
    download_button.click()
    time.sleep(3)
    driver.close()
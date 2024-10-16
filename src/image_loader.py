import requests
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains

def get_web_image(message, user, avatar, color):
    op = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : "/mnt/2tbdrive/projects/RoyBot/message-imgs",
            "browser.helperApps.neverAsk.saveToDisk": "text/csv"}

    op.add_argument("headless")
    op.add_argument("no-sandbox")
    op.enable_downloads = True
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
    name_box.click()
    driver.execute_script(f"document.getElementById('message-username-1').style.color = 'rgb({color.r}, {color.g}, {color.b})'")

    current_time = datetime.now().strftime("%I:%M %p")
    if datetime.now().hour < 10 or (datetime.now().hour > 12 and datetime.now().hour < 22):
        current_time = current_time[1:]
    # date_box.send_keys(f"Today at {datetime.now().hour if datetime.now().hour < 13 else datetime.now().hour - 12}:{datetime.now().minute if datetime.now().minute > 9 else "0" + str(datetime.now().minute)} {"AM" if datetime.now().hour < 13 else "PM"}")
    date_box.send_keys(f"Today at {current_time}")
    message_box.send_keys(message)
    avatar_box.send_keys(img_path)

    generate_button.click()
    time.sleep(1)

    #generated_image_link = driver.find_element(By.CLASS_NAME, "generated-image").get_attribute("src")
    #print(driver.get_downloadable_files())
    #driver.download_file(generated_image_link, "/mnt/2tbdrive/projects/RoyBot")

    # message_img_data = requests.get(generated_image_link).content
    # with open(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/{user}-message.jpeg", "wb") as message_file:
    #     message_file.write(message_img_data)

    download_button.click()
    time.sleep(3)
    driver.close()
import random
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import sys
import time
import requests

audioToTextDelay = 10
delayTime = 2
audioFile = "\\payload.mp3"
URL = "https://www.guerrillamail.com/compose"
SpeechToTextURL = "https://speech-to-text-demo.ng.bluemix.net/"

def delay():
    time.sleep(random.randint(2, 3))

def audioToText(audioFile):
    # opening https://speech-to-text-demo.ng.bluemix.net/ in a new text
    driver.execute_script('''window.open("","_blank")''')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(SpeechToTextURL)

    #sending the audio
    delay()
    audioInput = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    audioInput.send_keys(audioFile)

    time.sleep(audioToTextDelay)

    #getting the text
    text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')
    while text is None:
        text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')

    result = text.text

    #closing the windows
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result


try:
    # create chrome driver
    option = webdriver.ChromeOptions()
    option.add_argument('--disable-notifications')
    driver = webdriver.Chrome(os.getcwd() + "\\chromedriver.exe", options=option)
    delay()
    # go to website which have recaptcha protection
    driver.get(URL)
except Exception as e:
    sys.exit(
        "[-] Please make sure the chrome drivers are in the code folder")


email = driver.find_element_by_name("to")
subject = driver.find_element_by_name("subject")
message = driver.find_element_by_name("body")

# writing to the email
email.send_keys('email@gmail.com')
subject.send_keys("the subject")
message.send_keys("your message")

button = driver.find_element_by_id("send-button").click()

""" recaptcha code"""
delay()


def recaptch():
    #click the recaptch box
    g_recaptcha = driver.find_element_by_xpath("//*[contains(@src, 'https://www.google.com/recaptcha/api2/')]").click()
    iframes = driver.find_elements_by_tag_name('iframe')
    audioBtnFound = False
    audioBtnIndex = -1

    for index in range(len(iframes)):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name('iframe')[index]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(delayTime)
        try:
            audioBtn = driver.find_element_by_id("recaptcha-audio-button")
            audioBtn.click()
            audioBtnFound = True
            audioBtnIndex = index
            break
        except Exception as e:
            pass

    if audioBtnFound:
        try:
            while True:
                # get the mp3 audio file
                src = driver.find_element_by_id("audio-source").get_attribute("src")
                print("[INFO] Audio src: %s" % src)

                # download the mp3 audio file from the source
                urllib.request.urlretrieve(src, os.getcwd() + audioFile)

                # Speech To Text Conversion
                key = audioToText(os.getcwd() + audioFile)
                print("[INFO] Recaptcha Key: %s" % key)

                driver.switch_to.default_content()
                iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                driver.switch_to.frame(iframe)

                # key in results and submit
                inputField = driver.find_element_by_id("audio-response")
                inputField.send_keys(key)
                delay()
                inputField.send_keys(Keys.ENTER)
                delay()

                err = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]
                if err.text == "" or err.value_of_css_property('display') == 'none':
                    print("[INFO] Success!")
                    break

        except Exception as e:
            print(e)
            sys.exit("[INFO] Possibly blocked by google. Change IP,Use Proxy method for requests")
    else:
        sys.exit("[INFO] Audio Play Button not found! In Very rare cases!")

#call the recaptch
recaptch()
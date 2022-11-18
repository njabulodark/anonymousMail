import random
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import sys
import time
import requests
import chromedriver_autoinstaller

class Mail:
    def __init__(self):
        self.audioToTextDelay = 10
        self.delayTime = 2
        self.audioFile = "\\payload.mp3"
        self.URL = "https://www.guerrillamail.com/compose"
        self.SpeechToTextURL = "https://speech-to-text-demo.ng.bluemix.net/"
        self.driver = None
    
    def delay(self):
        time.sleep(random.randint(2, 3))

    def audioToText(self, audioFile):
        # opening https://speech-to-text-demo.ng.bluemix.net/ in a new text
        self.driver.execute_script('''window.open("","_blank")''')
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(self.SpeechToTextURL)

        #sending the audio
        self.delay()
        audioInput = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
        audioInput.send_keys(audioFile)

        #waiting for audio to text conversion
        time.sleep(self.audioToTextDelay)

        #getting the text
        text = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')
        while text is None:
            text = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')
        result = text.text

        #closing the windows
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        return result

    def recaptch(self):
        #click the recaptch box
        g_recaptcha = self.driver.find_element("xpath", "//*[contains(@src, 'https://www.google.com/recaptcha/api2/')]").click()
        iframes = self.driver.find_elements("tag_name",'iframe')
        audioBtnFound = False
        audioBtnIndex = -1

        for index in range(len(iframes)):
            self.driver.switch_to.default_content()
            iframe = self.driver.find_elements_by_tag_name('iframe')[index]
            self.driver.switch_to.frame(iframe)
            self.driver.implicitly_wait(self.delayTime)
            try:
                audioBtn = self.driver.find_element_by_id("recaptcha-audio-button")
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
                    src = self.driver.find_element_by_id("audio-source").get_attribute("src")
                    print("[INFO] Audio src: %s" % src)

                    # download the mp3 audio file from the source
                    urllib.request.urlretrieve(src, os.getcwd() + audioFile)

                    # Speech To Text Conversion
                    key = self.audioToText(os.getcwd() + self.audioFile)
                    print("[INFO] Recaptcha Key: %s" % key)

                    self.driver.switch_to.default_content()
                    iframe = self.driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                    self.driver.switch_to.frame(iframe)

                    # key in results and submit
                    inputField = self.driver.find_element_by_id("audio-response")
                    inputField.send_keys(key)
                    self.delay()
                    inputField.send_keys(Keys.ENTER)
                    self.delay()

                    err = self.driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]
                    if err.text == "" or err.value_of_css_property('display') == 'none':
                        print("[INFO] Success!")
                        break

            except Exception as e:
                print(e)
                sys.exit("[INFO] Possibly blocked by google. Change IP,Use Proxy method for requests")
        else:
            sys.exit("[INFO] Audio Play Button not found! In Very rare cases!")

    def connectToChrome(self):
        try:
            # create chrome driver
            chromedriver_autoinstaller.install()
            option = webdriver.ChromeOptions()
            option.add_argument('--disable-notifications')
            self.driver = webdriver.Chrome(options=option)
            self.delay()
            # go to website which have recaptcha protection
            self.driver.get(self.URL)
        except Exception as e:
            sys.exit(
                "[-] Please make sure the chrome drivers are in the code folder")
    

    def sendMail(self, email, subject, message):
        self.connectToChrome()
        #selecting all the user input fields
        f_email = self.driver.find_element("name","to")
        f_subject = self.driver.find_element("name","subject")
        f_message = self.driver.find_element("name","body")

        #filling the fields
        f_email.send_keys(email)
        f_subject.send_keys(subject)
        f_message.send_keys(message)

        #sending the mail
        button = self.driver.find_element("id", "send-button").click()

        """ recaptcha code"""
        self.delay()
        self.recaptch()

        #closing the driver
        self.driver.close()

if __name__ == "__main__":
    mail = Mail()
    mail.sendMail(input("Type the email you wanna send to: "), input("Type the subject: "), input("Type the message: "))
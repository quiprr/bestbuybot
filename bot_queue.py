import logging
import sys

import info
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from twilio.rest import Client

# Basic logging setup
# Change logging level as you wish
# DEBUG, INFO, WARNING, ERROR
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)    

# Function to send SMS message
def sendMessage(contents: str):
    try:
        logging.debug(f'Sending SMS message with contents "{contents}".')
        client.messages.create(to = info.twilio_toNumber, from_ = info.twilio_fromNumber, body = contents)
    except:
        logging.warning('Failed to send SMS message.')
        return

# Initialize Twilio Client
logging.debug('Initializing Twilio client...')
client = Client(info.twilio_accountSID, info.twilio_authToken)
sendMessage('Successfully initialized qbot client. Bot is running.')

# Initialize Web Driver
logging.debug('Initializing webdriver...')
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options = options, executable_path = info.chromeDriver)
driver.get(info.productLink)

isComplete = False

logging.debug('Starting main event loop.')
while not isComplete:
    # Find if item is in stock (add to cart button)
    try:
        logging.debug('Loading webpage for checks.')
        atcBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button"))
        )
    except:
        logging.warning('Add to cart button is not clickable. Refreshing...')
        driver.refresh()
        continue

    logging.info('Found add to cart button! Attempting to continue...')
    sendMessage('Item is in stock. Attempting purchase now.')

    try:
        # Enter product queue
        atcBtn.click()

        isComplete = True
        
        logging.info("Queue entry attempt was made.")
        sendMessage('Attempted to enter queue. Check for confirmation.')
    except:
        driver.get(info.productLink)
        logging.error("Error entering queue. Restarting...")
        sendMessage('Queue entry attempt was made, but failed.')
        continue

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
        # Add product to cart
        atcBtn.click()

        # Go to cart and proceed to checkout
        driver.get("https://www.bestbuy.com/cart")

        checkoutBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".checkout-buttons__checkout>button"))
        )
        checkoutBtn.click()
        logging.info("Successfully added to cart! Beginning checkout process...")

        # Fill in account details
        emailField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fld-e"))
        )
        emailField.send_keys(info.bb_email)

        pwField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fld-p1"))
        )
        pwField.send_keys(info.bb_password)

        # Click sign-in button to sign into account
        signInBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".cia-form__controls__submit"))
        )
        signInBtn.click()
        logging.info("Signing in to Best Buy account...")

        # Fill in card CVV
        cvvField = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "credit-card-cvv"))
        )
        cvvField.send_keys(info.bb_cvv)
        logging.info("Attempting to place order...")

        # Place the order
        placeOrderBtn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".button__fast-track"))
        )
        placeOrderBtn.click()

        isComplete = True
        
        logging.info("Order placement attempt was made.")
        sendMessage('Attempted to place order. Check for confirmation.')
    except:
        driver.get(info.productLink)
        logging.error("Error purchasing product. Restarting...")
        sendMessage('Item purchase attempt was made, but failed.')
        continue

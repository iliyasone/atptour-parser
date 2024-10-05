import json
import time
import platform

from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import logging

# Set up root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create a file handler that logs to 'log.txt'
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Set formatter for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to the root logger
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Set up atptour logger (main logger named 'logger')
logger = logging.getLogger('atptour')
logger.setLevel(logging.INFO)

# Propagate all messages to the root logger
logger.propagate = True

# Example usage
if __name__ == '__main__':
    logger.debug("This is a debug message from atptour logger.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

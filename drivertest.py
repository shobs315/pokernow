import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import pandas as pd

with webdriver.Chrome(options=Options(),
                        service=Service()) as driver:
        url = "https://www.pokernow.club/games/pglyWT62uDgl7WkaOmbX5dter?fbclid=IwAR0Uo3V8oSWC-utS30kfNYqEITPOWknlB5jRr_l6CGmNH0OGlr_lNO066xc"
        try:
            driver.get(url)
            actions = ActionChains(driver)
            actions.send_keys(Keys.CONTROL + 'l').perform()
            time.sleep(1)
            ledger_button = driver.find_element(By.CLASS_NAME, 'ledger-button')
            ledger_button.click()
            time.sleep(1)
            # Get the page source after the table is loaded
            page_source = driver.page_source

            # Close the webdriver
            driver.quit()
            print(page_source)
        except:
            print("hefljka")
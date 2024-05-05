from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By
import time
import pandas as pd
import streamlit as st

# Set up the Selenium webdriver (make sure to install the appropriate webdriver for your browser)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def get_ledger(url):
    driver.get(url)
    #time.sleep(1)
    actions = ActionChains(driver)
    actions.send_keys(Keys.CONTROL + 'l').perform()
    # Wait for the ledger table to load (you might need to adjust the sleep time based on the page load time)
    time.sleep(1)
    ledger_button = driver.find_element(By.CLASS_NAME, 'ledger-button')
    ledger_button.click()
    time.sleep(1)
    # Get the page source after the table is loaded
    page_source = driver.page_source


    # Close the webdriver
    driver.quit()

    # Parse the HTML content of the page
    soup = BeautifulSoup(page_source, 'html.parser')
    
    tables = soup.find_all('table')
    first = True
    players = []
    # Iterate through each table and print its content
    for table in tables:
        #print(table)
        # Extract table headers
        headers = [header.text.strip() for header in table.find_all('th')]
        if headers:
            print(headers)
        # Extract table rows
        rows = []
        for row in table.find_all('tr'):
            rows.append([cell.text.strip() for cell in row.find_all('td')])
        # Print table rows
        for row in rows:
            if first:
                titles = row
                first = False
            else:
                row[0] = row[0].split("@")[0]
                players.append(row)
    df = pd.DataFrame(players, columns=titles)
    return df

def generate_payouts(player_net_tuples):
    # Convert net amounts to floats
    player_net_tuples = [(name.strip(), float(net)) for name, net in player_net_tuples]
    
    # Initialize lists to store positive and negative net amounts
    positive_net = []
    negative_net = []
    
    # Separate positive and negative net amounts
    for name, net in player_net_tuples:
        if net > 0:
            positive_net.append((name, net))
        elif net < 0:
            negative_net.append((name, net))
    
    # Sort positive and negative net amounts by amount
    positive_net.sort(key=lambda x: x[1], reverse=True)
    negative_net.sort(key=lambda x: x[1])
    
    # Initialize list to store payouts
    payouts = []
    
    # Distribute positive net amounts to players with negative net amounts
    for payer, amount in positive_net:
        while amount > 0:
            receiver, debt = negative_net.pop(0)
            payment = min(amount, -debt)
            payouts.append((receiver, payer, payment))  # Reverse payer and receiver
            amount -= payment
            negative_net.append((receiver, debt + payment))
    
    return payouts


# URL of the Poker Now website
with st.form("URL"):
    url = st.text_input("Enter game URL")
    submitted = st.form_submit_button("Get Payouts")
if url:
    # Open the URL in the browser
    df = get_ledger(url)

    st.write("Ledger:")
    st.dataframe(df)
    player_net_tuples = list(df[['Player', 'Net↓']].to_records(index=False))[:-1]
    payouts = generate_payouts(player_net_tuples)
    
    for payer, receiver, amount in payouts:
        st.write(f"{payer.strip()} pays {receiver.strip()} {amount:.2f}")
import streamlit as st
import time
import pandas as pd
import heapq
 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup



def get_driver():
    service = Service()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def df_to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return value

def get_ledger(url):
    
    driver = get_driver()
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
    df.rename(columns={'Net↓':'Net'}, inplace=True)
    
    return df.iloc[:-1], list(df.iloc[-1])

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
            # Use a tuple with net amount as key to ensure sorting by net amount
            heapq.heappush(negative_net, (net, name))
    
    # Initialize list to store payouts
    payouts = []
    
    # Distribute positive net amounts to players with negative net amounts
    for receiver, amount in positive_net:
        while amount > 0 and negative_net:
            # Extract player with the smallest negative net amount
            debt, payer = heapq.heappop(negative_net)
            payment = min(amount, -debt)
            payouts.append((payer, receiver, payment))  # Reverse payer and receiver
            amount -= payment
            # If there is remaining debt, push it back to the heap
            if debt + payment < 0:
                heapq.heappush(negative_net, (debt + payment, payer))
                
    #sort so the same name has the payouts together            
    payouts.sort(key=lambda x: x[0])
    return payouts

st.set_page_config(page_title='PokerNow Payouts', page_icon=":spades:", layout='wide')

st.title("Poker Now Payouts :spades:")
st.write("This app can be used to generate the payouts for any poker game played on PokerNow. Just copy and paste the game link below")


with st.form("URL"):
    url = st.text_input("Enter game URL")
    submitted = st.form_submit_button("Get Payouts")
if url and submitted:

    df, total = get_ledger(url)
    
    
    
    player_net_tuples = list(df[['Player', 'Net']].to_records(index=False))
    
    payouts = generate_payouts(player_net_tuples)
    cols = ["", "Buy-In", "Buy-Out", "Stack"]

    # Create DataFrame from list and transpose it
    total_df = pd.DataFrame([total[:-1]], columns=cols)

    col1, col2 = st.columns(2)
    with col1:
        st.header("Ledger:")
        st.dataframe(df, hide_index=True)
        
        st.dataframe(total_df, hide_index=True)

    # Display payouts in the second column
    with col2:
        st.header("Payouts:")
        for payer, receiver, amount in payouts:
            st.write(f"{payer.strip()} pays {receiver.strip()} {amount:.2f}")

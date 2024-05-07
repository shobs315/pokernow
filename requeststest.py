import requests

# Replace 'your_poker_now_link_here' with the actual Poker Now link you want to send a request to
poker_now_link = 'https://www.pokernow.club/games/pglyWT62uDgl7WkaOmbX5dter?fbclid=IwAR3kS7F7azZ1UvHfws0P9meZGSON_MoA1KIzeBB2Sx-A0wIw-nztoob_zsU'

# Example request parameters
params = {
    'param1': 'value1',
    'param2': 'value2'
}

# Send a GET request
response = requests.get(poker_now_link)

# Print the response content
print(response.text)

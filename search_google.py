import requests

# url = 'https://onefootball.com/en/player/marcus-rashford-172006'
# url = 'https://scrapingclub.com/exercise/list_basic/?page=1'
url = 'https://www.google.com/search'

params = {'q':'onefootball'}

response = requests.get(url, params=params)

# print(response.headers) # это то что при запросе я передаю сайту
# print(response.content)
with open('search_google_page.html', 'w', encoding='utf-8') as file:
    file.write(response.text)

print(response.text)
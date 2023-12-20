import requests
from bs4 import BeautifulSoup

url = 'https://fbref.com/en/squads/df9a10a1/Portland-Thorns-FC-Stats'

response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.find('p')
    
    print(data)
else:
    print(f"Ошибка при запросе. Статус код: {response.status_code}")

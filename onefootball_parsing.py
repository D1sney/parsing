import requests
from bs4 import BeautifulSoup

url = 'https://onefootball.com/en/player/marcus-rashford-172006'
url2 = 'https://onefootball.com/en/player/inaki-williams-102887'

def parse_onefootball_player(player_url):
    # Отправляем запрос на веб-сайт
    response = requests.get(player_url)

    # print(response.text)
    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим интересующие нас элементы на странице
        player_name = soup.find('h1', class_='player-header__name')
        player_position = soup.find('p', class_='title-3-bold transfer-details-list__entry-title transfer-details-list__entry-subtitle--gray').text.strip()

        # Выводим результат
        print(f"Имя: {player_name}")
        print(f"Позиция: {player_position}")
    else:
        print(f"Ошибка при запросе. Статус код: {response.status_code}")

# Пример использования
parse_onefootball_player(url2)
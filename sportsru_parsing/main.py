import requests
from bs4 import BeautifulSoup
import pymysql
import json
import datetime
import time
from config import host, user, password, db_name

url1 = "https://www.sports.ru/marcus-rashford/"
url2 = "https://www.sports.ru/leroy-sane/"
url3 = "https://www.sports.ru/philip-foden/"
url4 = "https://www.sports.ru/ibrahimovic/"
url5 = "https://www.sports.ru/zidane/"
url6 = "https://www.sports.ru/erik-ten-hag/"
url7 = "https://www.sports.ru/scott-mctominay/"

team_url = "https://www.sports.ru/mu/team/"

league_url = "https://www.sports.ru/epl/table/"

urls = [url1, url2, url3, url4, url5, url6, url7]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
  }



def parse_league(league_url):
    # Отправляем запрос на веб-сайт
    response = requests.get(league_url, headers = headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'lxml') # html.parser

        # Находим список команд
        links = [team.find('a').get('href')+'team/' for team in soup.find('tbody').find_all('tr')]        
        return links
    else:
        print(f"Ошибка при запросе. Статус код: {response.status_code}")



def parse_team(team_url):
    print(team_url)
    # Отправляем запрос на веб-сайт
    response = requests.get(team_url, headers = headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'lxml') # html.parser

        # Находим список игроков
        links = [player.find('a').get('href') for player in soup.find('tbody').find_all('tr')]        
        return links
    else:
        print(f"Ошибка при запросе. Статус код: {response.status_code}")



def parse_player(player_url):
    # Отправляем запрос на веб-сайт
    response = requests.get(player_url, headers = headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'lxml') # html.parser

        # Находим карточку игрока
        player = soup.find('div', class_='box')

        img = None
        ru_name = None
        name = None
        season_games = None
        season_goals = None
        season_assists = None
        birthdate = None
        age = None
        nationality = None
        curent_club = None
        position = None
        height = None
        weight = None
        job_position = None

        img = player.find('img').get('src')
        ru_name = player.find('h1', class_='titleH1').text.strip()
        name = player.find('div', class_='descr').text.strip()
        
        stats = player.find_all('div', class_='item')
        if stats != []:
            for stat in stats:
                desc = stat.find('div', class_='line-th').text.strip()
                value = stat.find('div', class_='line-td').text.strip()
                try:
                    int(value)
                except:
                    value = 0
                if desc == 'Игры':
                    season_games = value
                elif desc == 'Голы':
                    season_goals = value
                elif desc == 'Голевые передачи':
                    season_assists = value
        
        items = player.find_all('tr')
        for item in items:
            desc = item.find('th').text.strip()
            value = item.find('td').text.strip()
            if desc == 'Родился':
                birthdate = value.split('|')[0].strip()
                age = int(value.split('|')[1].split(' ')[0].strip())
            elif desc == 'Гражданство':
                nationality = value
            elif desc == 'Клуб':    
                curent_club = value.split('|')[0].strip()
                position = value.split('|')[1].strip()
            elif desc == 'Амплуа':
                position = value
            elif desc == 'Рост и вес':
                height = int(value.split('|')[0].strip())
                weight = int(value.split('|')[1].strip())
            elif desc == 'Должность':
                job_position = value
        
        clubs = set()

        all_clubs = soup.find_all('div', class_='hide-field')
        if all_clubs != []:    
            for club in all_clubs:
                club_ = club.find('div', class_='hide-field')
                if club_ != None:
                    club_name = club_.find('a').text.strip()
                    clubs.add(club_name)
        
        clubs = json.dumps(list(clubs))

        # Выводим headers которые передаем сайту     
        # print(response.request.headers)

        return name, ru_name, convert_date(birthdate), age, nationality, curent_club, position, job_position, season_games, season_goals, season_assists, height, weight, clubs, img
    else:
        print(f"Ошибка при запросе. Статус код: {response.status_code}")



def sql_add_player(name, ru_name, birthdate, age, nationality, curent_club, position, job_position, season_games, season_goals, season_assists, height, weight, clubs, img):
    conn = None
    try:
        conn = pymysql.connect(
            host = host,
            port = 3306,
            user = user,
            password = password,
            database = db_name,
            cursorclass = pymysql.cursors.DictCursor
        )
        
        # cur = conn.cursor
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS Players ( id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
                        name TEXT,
                        ru_name TEXT,
                        birthdate DATE,
                        age INTEGER,
                        nationality TEXT,
                        current_club TEXT,
                        position TEXT,
                        job_position TEXT,
                        season_games INTEGER,
                        season_goals INTEGER,
                        season_assists INTEGER,
                        height INTEGER,
                        weight INTEGER,
                        clubs JSON,
                        img TEXT,
                        UNIQUE INDEX name_unique (name(255)))''')

        try:               
            with conn.cursor() as cur:
                cur.execute(f'''INSERT INTO Players (name, ru_name, birthdate, age, nationality, current_club, position, job_position, season_games, season_goals, season_assists, height, weight, clubs, img)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (name, ru_name, birthdate, age, nationality, curent_club, position, job_position, season_games, season_goals, season_assists, height, weight, clubs, img))
            conn.commit()
        except pymysql.IntegrityError as e:
            print(e)

    except Exception as ex:
        print(ex)
    finally:
        # Если соединение открыто, то закрываем его
        if conn != None:
            conn.close()



# Функция для преобразования строки с датой в объект datetime
def convert_date(date_str):
    months = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    try:
        parts = date_str.split()
        day = int(parts[0])
        month = months[parts[1].lower()]
        year = int(parts[2])
        return datetime.date(year, month, day)
    except:
        return None



# Пример использования
for t_url in parse_league(league_url):
    time.sleep(1)
    for url in parse_team(t_url):
        time.sleep(1)
        sql_add_player(*parse_player(url))
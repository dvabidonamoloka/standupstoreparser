import requests

from bs4 import BeautifulSoup
from bs4 import Comment


# playing with user agents
chrome_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
safari_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15"
headers = {"User-Agent": safari_ua}


# getting page
url = "http://standupstore.ru/"
response = requests.get(url, headers=headers)
html = response.content


# actual parsing
"""
#### Для работы парсера надо

1. гарантированно находить дату и время события, т.к. это будет идентификатор мероприятия  
    сейчас это хранится в пяти местах, можно искать каждое по очереди, если не найдены дата или время
    1. первый способ: через div t778__descr - блок, в котором лежит инфа, которая отображается на странице
            data-date="24 февраля, 21:30"

2. находить стоимость мероприятия
    1. первый способ: находить блок с ценой, но этого блока может не быть
            if event1.find('div', class_="js-product-price"):
                event_price = event1.find('div', class_="js-product-price").text
    2. второй способ:
            comment = event2.find(string=lambda text: isinstance(text, Comment))
            comment_soup = BeautifulSoup(comment, 'html.parser')
            event_price = comment_soup.find('a')['data-cost']

3. находить и сохранять афишу мероприятия
    1. первый способ: находить блок с картинкой и брать поле data-original
            event1.find('div', class_="js-product-img")["data-original"]
    2. второй способ: находить блок с картинкой, брать поле style и каким-то образом вытаскивать оттуда
    3. третий и четыверный способы аналогичны, но для дублирующего блока с картинками, пока нет смысла расписывать
    
4. находить и сохранять доступность билетов в виде булевого значения

5. находить и сохранять количество оставшихся мест, если указаны
"""
soup = BeautifulSoup(html,'html.parser')


events = soup.findAll('div', class_="t778__col")
event1 = events[0]
event2 = events[1]

date_and_time = event.find(class_="t778__descr").text
if event1.find('div', class_="js-product-price"):
    event_price = event1.find('div', class_="js-product-price").text



"""
thoughts on how parsing process should look like

import susp.db
import susp.events

html = ...
soup = ...
events = susp.events.all()

for event in events:
    when = get_event_datetime(event)                # if nothing found leaving this event
    if not when:
        continue
    price = get_event_price(event)                  # returns None if can't fetch
    poster = get_event_poster(event)                # returns None if can't fetch
    is_available = check_event_availability(event)  # returns None if can't fetch
    seats_left = fetch_remaining_tickets(event)     # returns None if can't fetch

    susp.db.save_event(when, price, poster, is_available, seats_left)
    # saves if event is new or updates if it's existing event
    # also can have some logic like if availability has changed from False to True
    # also need to place somewhere logic of notifying about new events
"""

# automating parsing of all pages
def get_all_events():
    """Iterates pages and gets events on each page."""
    pass
    # url = 
    # while ...:
    #     html = get_html(url)

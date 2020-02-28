import random
import re
import requests
import time

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
soup = BeautifulSoup(html,'html.parser')

events = soup.findAll('div', class_="t778__col")
event1 = events[0]
event2 = events[1]
event3 = BeautifulSoup("""<div class="t778__mark">5 мест</div>""", "html.parser")

"""
### Чтобы парсер заработал, надо

#### Найти все мероприятия на сайте
1. первый способ: найти все блоки класса "t778__col"
        events = soup.findAll('div', class_="t778__col")
2. второй способ: ??? - нужно еще посмотреть для надежности
        проверить классы t_col t_col_4 t_item js


#### Вытащить информацию о каждом мероприятии

1. гарантированно находить дату и время события, т.к. это будет идентификатор мероприятия  
    сейчас это хранится в пяти местах, может искать каждое по очереди, если не найдены дата или время
    1. первый способ: через поле data-date в закоментированной строке
    2. второй способ: через div t778__descr - блок, в котором лежит инфа, которая отображается на странице
            data-date="24 февраля, 21:30"
    строку можно превратить в datetime  

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
    1. первый способ (желаемый): через поле data-seats в закоментированной строке-ссылке, если мест 0, то билетов нет. Минус в том, что пока не понятно, всегда ли есть и будет закоментированная строка-ссылка
    2. второй способ: через слова "Места есть", "Мест нет" — минус в том, что иногда формулировка может отличаться, например "Осталось 3 места"

5. находить и сохранять количество оставшихся мест, если указаны
    1. первый способ (желаемый): через поле data-seats в закоментированной строке-ссылке, если мест 0, то билетов нет. Минус в том, что пока не понятно, всегда ли есть и будет закоментированная строка-ссылка

примерная схема работы

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
    poster_url = get_event_poster_url(event)        # returns None if can't fetch
    is_available = check_event_availability(event)  # returns None if can't fetch
    seats_left = fetch_remaining_tickets(event)     # returns None if can't fetch

    susp.db.save_event(when, price, poster_url, is_available, seats_left)
    # saves if event is new or updates if it's existing event
    # also can have some logic like if availability has changed from False to True
    # also need to place somewhere logic of notifying about new events
"""

# automating parsing of all pages
def get_all_events():
    """Iterates pages and returns events from all pages."""

    total_events = []
    page_num = 1

    page_events = True
    while page_events:
        page_url = 'https://standupstore.ru/page/{}/'.format(page_num)
        page_response = requests.get(page_url, headers=headers)
        page_html = page_response.content
        page_soup = BeautifulSoup(page_html, 'html.parser')

        page_events = page_soup.findAll('div', class_="js-product")
        if not page_events:
            page_events = page_soup.findAll('div', class_="t778__col")
        if not page_events:
            page_events = page_soup.findAll('div', class_="t778__wrapper")

        if page_events:
            total_events.extend(page_events)
            page_num += 1
            time.sleep(random.randint(5, 10))
        # TODO: make functions for notification and saving html for further analysis
        # else:
        #     if not total_events:
        #         notify("No events were found!")  # letting know, something 
        #         save_html(page_html)             # for further checking

    return total_events


def get_event_datetime_str(event):
    """Some text here."""
    # first trying with comment, then trying with t778__descr
    # also here can be found some other comment, so need some assertion check here
    comment = event.find(string=lambda text: isinstance(text, Comment))
    comment_soup = BeautifulSoup(comment, 'html.parser')
    event_datetime_str = comment_soup.find('a').get('data-date', None)

    if not event_datetime_str:
        try:
            event_datetime_str = event.find(class_="t778__descr").text
        except AttributeError:  # if nothing found
            pass

    return event_datetime_str


def get_event_price(event):
    """Returns price of given event."""

    event_price = None

    comment = event.find(string=lambda text: isinstance(text, Comment))
    if comment:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        link = comment_soup.find('a')
        if link:
            event_price = link.get('data-cost', None)

    if not event_price:
        # price_div = event.find('div', class_="js-product-price") - which class is better?1
        price_div = event.find('div', class_="t778__price")
        if price_div:
            event_price = price_div.text

    return event_price if event_price else None


def get_event_poster_url(event):
    """Returns poster url of given event."""

    event_poster_url = None
    
    poster_div = event.find('div', class_="js-product-img")
    event_poster_url = poster_div.get("data-original")
    
    if not event_poster_url:
        poster_div = event.find('div', class_="t778__bgimg")
        event_poster_url = poster_div.get("data-original")

    return event_poster_url


def is_available(event):
    """Returns availability of given event."""

    is_available = None

    comment = event.find(string=lambda text: isinstance(text, Comment))
    if comment:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        link = comment_soup.find('a')
        if link:
            seats_num = link.get('data-seats')
            if seats_num:
                is_available = bool(int(seats_num))

    if is_available is None:
        availibility_mapping = {
            "Нет мест": False,
            "Места есть": True,
            "\d мест": True,
        }
        seats_div = event.find("div", class_="t778__mark")
        if seats_div:
            for key in availibility_mapping:
                if re.match(key, seats_div.text):
                    is_available = availibility_mapping[key]
                    break

    return is_available


def get_remaining_tickets(event):
    """Returns number of remaining tickets for given event."""

    remaining_tickets = None

    comment = event.find(string=lambda text: isinstance(text, Comment))
    if comment:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        link = comment_soup.find('a')
        if link:
            seats_num = link.get('data-seats')
            if seats_num:
                remaining_tickets = int(seats_num)

    if remaining_tickets is None:
        seats_div = event.find("div", class_="t778__mark")
        if seats_div:
            pattern = "\d мест"
            if re.match(pattern, seats_div.text):
                remaining_tickets = int(seats_div.text.split(' ')[0])

    return remaining_tickets

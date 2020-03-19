import random
import re
import requests
import time

from bs4 import BeautifulSoup
from bs4 import Comment


def get_all_events():
    """Iterates pages and returns events from all pages."""

    # playing with user agents
    chrome_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    safari_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15"
    headers = {"User-Agent": safari_ua}

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


def get_event_availability(event):
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


def get_event_url(event):
    """Returns link to an event."""

    event_url = None

    link_tag = event.find("a")
    if link_tag:
        event_url = link_tag["href"]

    return event_url


# TODO:
# продумать, что делать, если я пытаюсь сохранить информацию о мероприятии, а часть данных уже есть
# надо ли перезаписывать или наоборот игнорировать?
# может ли измениться цена? - пока будем считать, что не может
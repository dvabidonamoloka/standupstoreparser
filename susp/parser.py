import logging
import random
import re
import requests
import time

import susp.notifications

from bs4 import BeautifulSoup
from bs4 import Comment
from mongoengine.errors import DoesNotExist

from susp.event import Event

LOG = logging.getLogger(__name__)


def get_all_events():
    """Iterates pages and returns events from all pages."""

    # playing with user agents
    # chrome_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 \
    #     (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    safari_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 \
        (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15"
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
            r"\d мест": True,
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
                remaining_tickets = seats_num

    if remaining_tickets is None:
        seats_div = event.find("div", class_="t778__mark")
        if seats_div:
            pattern = r"\d мест"
            if re.match(pattern, seats_div.text):
                remaining_tickets = seats_div.text.split(' ')[0]

    if remaining_tickets is None:
        seats_div = event.find("div", class_="t778__mark")
        if seats_div:
            remaining_tickets = seats_div.text

    return remaining_tickets


def get_event_url(event):
    """Returns link to an event."""

    event_url = None

    link_tag = event.find("a")
    if link_tag:
        event_url = link_tag["href"]

    return event_url


def check_events():
    """Main parsing function."""

    try:
        LOG.info("Parsing events...")
        events = susp.parser.get_all_events()

        LOG.debug(f"Got {len(events)} events")

        processed_events_count = 0
        new_events_count = 0
        became_available_events_count = 0

        for event in events:
            datetime_str = susp.parser.get_event_datetime_str(event)
            if not datetime_str:
                LOG.error(f"Couldn't fetch datetime_str for event: {event}, skipping...")
                continue

            LOG.debug(f"Processing event on {datetime_str}...")

            is_available = susp.parser.get_event_availability(event)
            price = susp.parser.get_event_price(event)
            poster_url = susp.parser.get_event_poster_url(event)
            seats_left = susp.parser.get_remaining_tickets(event)
            url = susp.parser.get_event_url(event)

            LOG.debug(f"Event availability: {is_available}")

            try:
                saved_event = Event.objects.get(datetime_str=datetime_str)
                if is_available and not saved_event.is_available:
                    LOG.debug("Updating saved event...")
                    saved_event.is_available = is_available
                    saved_event.price = price
                    saved_event.seats_left = seats_left
                    saved_event.save()
                    susp.notifications.make_notification(saved_event, is_new=False)
                    became_available_events_count += 1

            except DoesNotExist:
                LOG.debug("Creating new event...")
                event = Event(
                    datetime_str=datetime_str,
                    price=price,
                    poster_url=poster_url,
                    is_available=is_available,
                    seats_left=seats_left,
                    url=url,
                )
                event.save()
                susp.notifications.make_notification(event, is_new=True)
                new_events_count += 1

            processed_events_count += 1

        LOG.info("Parsing finished")
        LOG.info(f"Processed events:        {processed_events_count}")
        LOG.info(f"New events:              {new_events_count}")
        LOG.info(f"Events available again:  {became_available_events_count}")

    except Exception as e:
        LOG.exception(f"While checking events exception happened: {e}")
        raise

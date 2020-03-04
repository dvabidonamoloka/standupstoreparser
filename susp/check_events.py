"""Main parsing script."""

import susp.db
import susp.parser
from susp.event import Event


def main():
    events = susp.parser.get_all_events()

    for event in events:
        datetime_str = susp.parser.get_event_datetime_str(event)
        if not datetime_str:
            continue

        price = get_event_price(event)
        poster_url = get_event_poster_url(event)
        is_available = check_event_availability(event)
        seats_left = fetch_remaining_tickets(event)
        url = get_event_url(event)

        # existing_event = get_event_from_db(datetime_str)
        saved_event = Event.one(datetime_str)  # checking if event exists in db, if exists, returns event object
        if saved_event:
            saved_event.update_availability(is_available)  # this func calls notification func if needed
        else:
            Event.create(datetime_str, price, poster_url, is_available, seats_left, url)


if __name__ == "__main__":
    main()

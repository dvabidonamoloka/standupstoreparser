#! /usr/bin/env python

"""Main parsing script."""

import logging

import susp.parser
import susp.utils

from mongoengine.errors import DoesNotExist

from susp.event import Event

LOG = susp.utils.make_logger()


def main():
    """Main parsing function."""

    LOG.info("Parsing events...")
    # TODO: make calls with different user agent and maybe sometimes use proxy
    events = susp.parser.get_all_events()

    processed_events_count = 0
    new_events_count = 0
    became_available_events_count = 0

    for event in events:
        datetime_str = susp.parser.get_event_datetime_str(event)
        if not datetime_str:
            LOG.error(f"Couldn't fetch datetime_str for event: {event}, skipping...")
            continue

        is_available = susp.parser.check_event_availability(event)

        try:
            saved_event = Event.objects.get(datetime_str=datetime_str)
            if is_available and not saved_event.is_available:
                susp.notifications.available_again(saved_event)
                became_available_events_count += 1

        except DoesNotExist:
            price = susp.parser.get_event_price(event)
            poster_url = susp.parser.get_event_poster_url(event)
            seats_left = susp.parser.get_remaining_tickets(event)
            url = susp.parser.get_event_url(event)

            event = Event(
                datetime_str=datetime_str,
                price=price,
                poster_url=poster_url,
                is_available=is_available,
                seats_left=seats_left,
                url=url,
            )
            susp.notifications.new_event(event)
            new_events_count += 1

        processed_events_count += 1

    LOG.info("Parsing finished")
    LOG.info(f"Processed events:        {processed_events_count}")
    LOG.info(f"New events:              {new_events_count}")
    LOG.info(f"Events available again:  {became_available_events_count}")


if __name__ == "__main__":
    main()

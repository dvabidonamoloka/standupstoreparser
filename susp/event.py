"""Describes event model."""

from susp.notifications import post_to_channel


class Event():

    def __init__(self):
        """Check as in c2."""
        pass

    def create(self, datetime_str, price, poster_url, is_available, seats_left, url):
        """Actions on event creation."""
        message = ""
        post_to_channel(message)  # sending notification about new event
        pass

    def one(self):
        """Returns event as instance of class from db or None if event doesn't exist."""
        pass

    def update_availability(self, is_available):
        """Notifies if event were unavailable and became available."""
        pass
"""Describes event model."""

from mongoengine import (
    connect,
    BooleanField,
    Document,
    IntField,
    StringField,
)
from mongoengine.errors import NotUniqueError, DoesNotExist

# db connection
connect('susp', host='mongodb')


class Event(Document):
    """Represents event document."""

    meta = {'collection': 'events'}

    datetime_str = StringField(required=True, unique=True)
    price = StringField()
    poster_url = StringField()
    is_available = BooleanField()
    seats_left = StringField()
    url = StringField()

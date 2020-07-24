import logging

import telegram

from susp import settings


LOG = logging.getLogger(__name__)


def post_to_channel(message):
    '''Creates bot and sends message to the channel'''

    LOG.info('Connecting to the bot and posting message to the channel')

    mybot = telegram.Bot(token=settings.TOKEN)
    mybot.send_message(chat_id=settings.CHAT_ID, text=message, parse_mode='Markdown')

    LOG.info('Message posted to the channel')


def generate_event_message(event, is_new):
    '''
    Creates message to notificate about new event or
    about the newly available event.
    '''

    LOG.debug('Generating event message')

    if event.url or event.poster_url:
        date = event.datetime_str or 'Уточните дату на сайте'
        price = event.price or 'Уточните цену на сайте'
        seats = event.seats_left or 'Неизвестно'
        poster_url = event.poster_url  # if poster_url is None, space symbol will be ignored by telegram
        url = event.url or 'https://standupstore.ru/'

        message = f'Дата:[ ]({poster_url}){date}\nЦена: {price}\nОсталость мест: {seats}\n[Купить билеты]({url})'
        if not is_new:
            message = 'Билеты снова в продаже!\n' + message

        LOG.debug('Message created')
    else:
        LOG.error('Unable to generate a message: event url and poster url are missing')
        message = None

    return message


def make_notification(event, is_new=False):
    '''Creates message and posts it to the channel.'''

    message = generate_event_message(event, is_new)
    if message:
        post_to_channel(message)

import logging
import settings
import telegram


LOG = logging.getLogger(__name__)


def post_to_channel(message):
    '''Creates bot and sends message to the channel'''

    LOG.info('Connecting to the bot and posting message to the channel')

    mybot = telegram.Bot(token=settings.TOKEN, request=settings.REQPROXY)
    mybot.send_message(chat_id=settings.CHAT_ID, text=message, parse_mode='Markdown')

    LOG.info('Message posted to the channel')

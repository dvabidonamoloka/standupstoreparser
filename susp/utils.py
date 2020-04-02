import logging
import logging.handlers

from susp import settings


def make_logger():
    '''
    Creats and sets logger configurations.

    Note: use LOG.error(message, exc_info=True) or
    LOG.exception(message) to log traceback
    '''

    logger = logging.getLogger('susp')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('susp.log')
    # TODO: make mutable subject in SMTPHandler to know right away what kind of error came
    mh = logging.handlers.SMTPHandler(
        mailhost=(settings.SMPT_SERVER, settings.SMPT_PORT),
        fromaddr=settings.EXCEPTIONS_EMAIL_FROM,
        toaddrs=settings.EXCEPTIONS_EMAIL_TO,
        subject='Standupstore parser catched an exception',
        credentials=(settings.EXCEPTIONS_EMAIL_FROM, settings.SMPT_PASSWORD),
        secure=()
    )
    mh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(pathname)s - %(levelname)s - %(message)s')
    exception_formatter = logging.Formatter('%(asctime)s - %(pathname)s - %(message)s')
    fh.setFormatter(formatter)
    mh.setFormatter(exception_formatter)
    logger.addHandler(fh)
    logger.addHandler(mh)

    return logger

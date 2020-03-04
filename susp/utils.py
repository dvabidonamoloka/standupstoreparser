import logging


def make_logger():
    '''Creats and sets logger configurations'''

    logger = logging.getLogger('susp')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('susp.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

#! /usr/bin/env python

"""Entry point for the parser."""

import threading
import time

import schedule

import susp.parser
import susp.utils

LOG = susp.utils.make_logger()

import susp.notifications


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def run_parser():
    """Run infinite loop for checking events periodically.
    Documentation for "Schedule": http://schedule.readthedocs.io/.
    """

    schedule.every(300).to(600).seconds.do(run_threaded, susp.parser.check_events)

    LOG.info("Starting periodic events checking...")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_parser()

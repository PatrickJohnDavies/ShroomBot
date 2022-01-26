
import logging
from typing import Optional
from fastapi import FastAPI
import uvicorn
import requests
import threading
import queue
from enum import Enum, auto

CONTROLLER_PORT = 8000
ARM_PORT = 8001
VISION_PORT = 8002


class State(Enum):
    INITIALIZE = auto()
    IDLE = auto()
    START = auto()
    STARTED = auto()
    STOP = auto()
    STOPPED = auto()


# Create logger for this module
logger = logging.getLogger(__name__)
queue = queue.Queue()
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/start")
def read_item():
    logger.debug('@app.get("/start")')
    queue.put('start')
    # r = requests.get(f'http://127.0.0.1:{VISION_PORT}/start')
    return {"ok"}


@app.get("/stop")
def read_item():
    logger.debug('@app.get("/stop")')
    queue.put('stop')
    return {"ok"}


class Controller():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)
        # self.queue = queue
        self.state = State.INITIALIZE
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        do_run = True
        while do_run:
            # Process the command
            if self.state == State.INITIALIZE:
                self.logger.debug('Entered State.INITIALIZE')
                self.state = State.IDLE
            elif self.state == State.IDLE:
                # self.logger.debug('Entered State.IDLE')
                # self.logger.debug(f'queue size = {queue.qsize()}')
                if not queue.empty() and queue.get() == 'start':
                    self.state = State.START
            elif self.state == State.START:
                logger.debug('Entered State.START')
            elif self.state == State.STARTED:
                logger.debug('Entered State.STARTED')
                r = requests.post(f'http://127.0.0.1:{ARM_PORT}/pick', data={'x': '0.100', 'y': '0.200'})
            elif self.state == State.STOP:
                logger.debug('Entered State.STOP')
            elif self.state == State.STOPPED:
                logger.debug('Entered State.STOPPED')


if __name__ == "__main__":
    # create formatter
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)
    ch.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.debug('Created logger')

    # Start the controller
    controller = Controller()

    # Start the API server
    uvicorn.run(app, host="127.0.0.1", port=CONTROLLER_PORT, log_level="info")
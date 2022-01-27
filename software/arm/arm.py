from http.client import OK
from typing import Optional
from pydantic import BaseModel
import logging
from operator import truediv
from typing import Optional
from fastapi import FastAPI
import uvicorn
# import requests
import threading
import queue
from enum import Enum, auto
import time

ARM_PORT = 8001


class Coordinate(BaseModel):
    x: int
    y: int


# Create logger for this module
logger = logging.getLogger(__name__)
queue = queue.Queue()
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/pick/")
async def create_pick(coordinate: Coordinate):
    ## TODO: Create a background test that executes the pick motions
    ## TODO: Define status codes that help us return appropriately
    logger.debug("We are picking {},{}".format(coordinate.x, coordinate.y))
    queue.put(coordinate)
    return {"ok"}


class Arm():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        do_run = True
        while do_run:
            # Pull a coordinate from the queue and execute a pick on it
            if not queue.empty():
                coordinate = queue.get()
                self.pick(coordinate)

    # Function to pick a mushroom
    def pick(self, coordinate):
        pass


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
    controller = Arm()

    # Start the API server
    uvicorn.run(app, host="127.0.0.1", port=ARM_PORT, log_level="info")
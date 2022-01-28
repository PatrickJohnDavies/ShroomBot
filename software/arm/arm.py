from http.client import OK
import re
from tkinter import E
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
import requests

ARM_PORT = 8001
MOONRAKER_PORT = 7125

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


@app.post("/pick")
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
        # mm_x, mm_y = coordinate['x'], coordinate['y']
        mid = 1 # to set

        filename = f"mushroom_{mid}.gcode"
        # Create a file representing the gcode of the mushroom id
        f = open("/home/pi/gcode_files/{}".format(filename), "w")
        f.write("Hello world!")
        f.close()

        # Send the gcode file to job queue
        try:
            r = requests.post(f"http://localhost:{MOONRAKER_PORT}/server/job_queue/job?filenames={filename}")
            logger.debug("Succesfully sent file to queue")
        except BaseException as err:
            self.logger.error("FAILED TO ADD TO JOB QUEUE")

        # Validate the status andof the queue
        try:
            r = requests.get(f"http://localhost:{MOONRAKER_PORT}/server/job_queue/status")
            jobs = r.json()['queued_jobs']
            if len(jobs) == 0:
                self.logger.error("error: We are fuckedddddd no jobs were found")
            else:
                print(jobs)
                self.logger.debug("Successfuly seend the job to the queue")
        except BaseException as err:
            self.logger.error(err)
            self.logger.error("FAILED TO SEND REQUEST FOR JOB QUEUE")

        # # Start the job queue
        # try:
        #      r = requests.post(f"http://localhost:{MOONRAKER_PORT}/server/job_queue/start")
        # except:
        #      self.logger.error("FAILED TO START THE JOB QUEUE")

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
    uvicorn.run(app, host="0.0.0.0", port=ARM_PORT, log_level="info")
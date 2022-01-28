from http.client import OK
from numbers import Rational
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
import RPi.GPIO as GPIO
import time

ARM_PORT = 8001


class Coordinate(BaseModel):
    x: float
    y: float
    z: float


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
        self.position = Coordinate(x=0, y=0, z=0)

        # m0dir_pin = 21
        # m0step_pin = 20
        # m0limit_pin = 4
        # axis_radius = StepperDriver(m0dir_pin, m0step_pin, m0limit_pin, (360/1.8)/0.002)
        
        m1dir_pin = 21
        m1step_pin = 20
        m1limit_pin = 4
        self.stepper_radius = StepperDriver(m1dir_pin, m1step_pin, m1limit_pin, (360/1.8)/0.002)
        
        # m2dir_pin = 21
        # m2step_pin = 20
        # m2limit_pin = 4
        # axis_height = StepperDriver(m2dir_pin, m2step_pin, m2limit_pin, (360/1.8)/0.002)

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

class StepperDriver:
    def __init__(self, dir_pin, step_pin, limit_pin, ratio):
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.limit_pin = limit_pin
        self.ratio = ratio
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.limit_pin, GPIO.IN)
        self.direction = 0
    
    def step(self):
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(self.step_pin, GPIO.LOW)

    def steps(self, steps_n):
        dir = 1
        if steps_n < 0:
            dir = 0
            steps_n = -1 * steps_n
        self.setDirection(dir)
        for step_i in range(steps_n):
            if self.direction == 0 and self.isLimited():
                return 1    
            self.step()
        return 0

    def setDirection(self, is_forward):
        self.direction = is_forward
        GPIO.output(self.dir_pin, is_forward)

    def isLimited(self):
        return not GPIO.input(self.limit_pin)

    def home(self):
        self.setDirection(0)
        while(not self.isLimited()):
            self.step()

    def move(self, distance):
        steps_n = distance * self.ratio
        self.steps(int(steps_n))


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

    GPIO.setmode(GPIO.BCM)

    m1dir_pin = 21
    m1step_pin = 20
    m1limit_pin = 4
    axis_radius = StepperDriver(m1dir_pin, m1step_pin, m1limit_pin, (360/1.8) / (2*3.14*0.005))
    axis_radius.home()
    axis_radius.move(0.5)
    while(True):
        axis_radius.move(0.2)
        axis_radius.move(-0.2)

    # # Start the controller
    # arm = Arm()
    # coordinate = Coordinate(x=0.1, y=0.05, z=0)
    # queue.put(coordinate)

    # Start the API server
    uvicorn.run(app, host="0.0.0.0", port=ARM_PORT, log_level="info")
    
    GPIO.cleanup()
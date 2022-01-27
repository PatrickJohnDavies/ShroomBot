
# Install libraries with:
#   python -m pip install fastapi, uvicorn, requests
# Test routes with ie curl hostname.local:8000/lights/on

import logging
from typing import Optional
from fastapi import FastAPI
import uvicorn
import requests
import threading
import queue
from enum import Enum, auto
import time
import RPi.GPIO as GPIO
# Neopixels
import time
import board
import neopixel

# CONTROLLER_HOSTNAME = 'shroombot_controller'
CONTROLLER_HOSTNAME = '127.0.0.1'
CONTROLLER_PORT = 8000
# ARM_HOSTNAME = 'shroombot_controller'
ARM_HOSTNAME = '127.0.0.1'
ARM_PORT = 8001
# VISION_HOSTNAME = 'WhatIsItsHostname?'
VISION_HOSTNAME = '127.0.0.1'
VISION_PORT = 8002

class State(Enum):
    INITIALIZE = auto()
    IDLE = auto()
    RUNNING = auto()
    STOPPED = auto()


# Create logger for this module
logger = logging.getLogger(__name__)
# Queue for passing data from FastAPI to Controller
queue = queue.Queue()

# Neopixel setup
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D10
num_pixels = 16
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

# IO pins
fan_pin = 9 # Broadcom pin 9

# API routes
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/start")
def read_item():
    logger.debug('@app.get("/start")')
    queue.put('/start')
    # r = requests.get(f'http://127.0.0.1:{VISION_PORT}/start')
    return {"ok"}

@app.get("/stop")
def read_item():
    logger.debug('@app.get("/stop")')
    queue.put('/stop')
    return {"ok"}

@app.get("/lights/on")
def read_item():
    logger.debug('@app.get("/lights/on")')
    pixels.fill((255, 0, 0))
    pixels.show()
    return {"ok"}

@app.get("/lights/off")
def read_item():
    logger.debug('@app.get("/lights/off")')
    pixels.fill((0, 0, 0))
    pixels.show()
    return {"ok"}

@app.get("/fan/on")
def read_item():
    logger.debug('@app.get("/fan/on")')
    GPIO.output(fan_pin, GPIO.HIGH)
    return {"ok"}

@app.get("/fan/off")
def read_item():
    logger.debug('@app.get("/fan/off")')
    GPIO.output(fan_pin, GPIO.LOW)
    return {"ok"}
    


class Controller():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)
        # self.queue = queue
        self.state = State.INITIALIZE
        self.curr_time = time.perf_counter()
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        do_run = True
        while do_run:
            time.sleep(1)
            # Process the command
            if self.state == State.INITIALIZE:
                self.logger.debug('Entered State.INITIALIZE')
                self.state = State.IDLE
            elif self.state == State.IDLE:
                # self.logger.debug('Entered State.IDLE')
                # self.logger.debug(f'queue size = {queue.qsize()}')
                if not queue.empty() and queue.get() == '/start':
                    self.state = State.RUNNING
            elif self.state == State.RUNNING:
                # Check if 10 seconds have passed and call the computer vision module
                if time.perf_counter() - self.curr_time >= 10:
                    logger.debug("Executing the detect and pick operation")
                    self.curr_time = time.perf_counter()
                    try:
                        potential_coordinates = self.detect()
                        logger.debug(f'potential_coordinates = {potential_coordinates}')
                        if potential_coordinates == None:
                            continue
                        self.pick(potential_coordinates)
                    except:
                        continue
                    
            elif self.state == State.STOPPED:
                logger.debug('Entered State.STOPPED')

    def detect(self) -> Optional[dict]:
        r = requests.get(f'http://{VISION_HOSTNAME}:{VISION_PORT}/mushrooms/random')
        mushroom_coordinates = r.json()['frame']
        if len(mushroom_coordinates) == 0:
            return None
        return mushroom_coordinates[0]

    def pick(self, coordinates) -> Optional[int]: # int represents status code
        r = requests.post(f'http://{ARM_HOSTNAME}:{ARM_PORT}/pick', data=coordinates)
        status_code = r.json()['status_code']
        if status_code == 0:
            print("Arm is moving toward target")
        elif status_code == 1:
            print("Arm is busy")
        elif status_code:
            print("There was an error with picking the")

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
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, GPIO.LOW)

    # Start the controller
    controller = Controller()
    
    # Start the API server
    # uvicorn.run(app, host="127.0.0.1", port=CONTROLLER_PORT, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=CONTROLLER_PORT, log_level="info")
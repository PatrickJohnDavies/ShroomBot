from http.client import OK
from typing import Optional
from enum import Enum
from service import get_n_frame, get_mushrooms_coordinates, get_mushrooms_with_connected_components
from fastapi import FastAPI
import uvicorn
import logging
import numpy as np

CONTROLLER_PORT = 8000
ARM_PORT = 8001
VISION_PORT = 8002

app = FastAPI()
logger = logging.getLogger(__name__)
# create formatter
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(log_formatter)
logger.addHandler(ch)
ch.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)


class AnalyzeStatus(Enum):
    OK = 1
    IDLE = 2
    ERROR = 3


@app.get("/")
async def read_root():
    return {"JoJo": "World"}


@app.get("/mushrooms")
async def read_mushrooms():
    '''Returns mushroom id, centroid X and Y coordinates
    Eg. (mushroom_num, cX, cY)
    '''
    logger.debug('@app.get("/mushrooms")')
    img = get_n_frame(1)
    mushrooms_coordinates = get_mushrooms_with_connected_components(img)
    logger.debug(f'mushrooms_coordinates: {mushrooms_coordinates}')
    return {'frame': str(mushrooms_coordinates)}


@app.get("/mushrooms/random")
async def read_mushrooms():
    '''Returns mushrooms caps coordinates on an image in
    '''
    logger.debug('@app.get("/mushrooms/random")')
    mushrooms_coordinates = np.array([0.1, 0.2])
    logger.debug(f'mushrooms_coordinates: {mushrooms_coordinates}')
    return {'frame': str(mushrooms_coordinates)}


@app.get("/analyze")
async def read_analyze(item_id: int, q: Optional[str] = None):
    logger.debug('@app.get("/analyze")')
    # call background tasks that calls the cv module that processes the image and send back and image
    # cc: https://fastapi.tiangolo.com/tutorial/background-tasks/ 
    return {"status": OK}


if __name__ == "__main__":
    # Start the API server
    uvicorn.run(app, host="127.0.0.1", port=VISION_PORT, log_level="info")

from http.client import OK
from typing import Optional
from enum import Enum
from service import get_n_frame, get_mushrooms_coordinates
from fastapi import FastAPI

app = FastAPI()

CONTROLLER_PORT = 8000
ARM_PORT = 8001
VISION_PORT = 8002

class AnalyzeStatus(Enum):
    OK = 1
    IDLE = 2
    ERROR = 3

@app.get("/")
async def read_root():
    return {"JoJo": "World"}

@app.get("/mushrooms")
async def read_mushrooms():
    '''Returns mushrooms caps coordinates on an image in 
    '''
    img = get_n_frame(1)
    mushrooms_coordinates = get_mushrooms_coordinates(img)
    return {'frame': str(mushrooms_coordinates)}

@app.get("/analyze")
async def read_analyze(item_id: int, q: Optional[str] = None):
    # call background tasks that calls the cv module that processes the image and send back and image
    # cc: https://fastapi.tiangolo.com/tutorial/background-tasks/ 
    return {"status": OK}

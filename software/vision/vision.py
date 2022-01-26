from http.client import OK
from typing import Optional
from enum import Enum

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
    return {"Hello": "World"}

@app.get("/mushrooms")
async def read_mushrooms(item_id: int, q: Optional[str] = None):
    # returns maintaiend 
    return {"mushrooms": [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]}

@app.get("/analyze")
async def read_analyze(item_id: int, q: Optional[str] = None):
    # call background tasks that calls the cv module that processes the image and send back and image
    # cc: https://fastapi.tiangolo.com/tutorial/background-tasks/ 
    return {"status": OK}


print("this is awesome")
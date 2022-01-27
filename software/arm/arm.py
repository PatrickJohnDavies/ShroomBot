from http.client import OK
from typing import Optional
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()

CONTROLLER_PORT = 8000
ARM_PORT = 8001
VISION_PORT = 8002

class Coordinate(BaseModel):
    x: int
    y: int

@app.post("/pick/")
async def create_pick(coordinate: Coordinate):
    ## TODO: Create a background test that executes the pick motions
    ## TODO: Define status codes that help us return appropriately
    print("We are picking {},{}".format(coordinate.x, coordinate.y))


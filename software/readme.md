#### Setup environment 

$ python3 -m pip install --user --upgrade pip

$ python3 -m venv shrooms

$ source shrooms/bin/activate 

$ python3 -m pip install -r requirements.txt

### Vision Specs

Camera is 3-channeled, 960 x 1280 pixels, 8-bit per pixel.

Mushrooms endpoint returns vector of found mushrooms.

Each vector is encoded as 3 or 4 element floating-point vector (x,y,radius).

CV2 is BGR (not RGB).

For HSV, hue range is [0,179], saturation range is [0,255], and value range is [0,255].  

### Methodology to extract mushroom from image
0. Receive request from microcontroller endpoint
1. Take 1 frame from video
2. Preprocess image: Remove noise-> filter mushroom color range (mask)-> invert mask -> greyscale -> threshold pixels
3. Localize mushrooms using connected components algorithm
4. Get statistics from connected components (centroids, area, components)
5. Draw square around each mushroom and on centroid 
6. Send mushrooms centroids to robot (mushroom_id, x,y) 

![alt text](/software/vision/data/00_v1_brown_shrooms.jpeg?raw=true "Brown shrooms test")


#### Setup environment 

$ python3 -m pip install --user --upgrade pip

$ python3 -m venv shrooms

$ source shrooms/bin/activate 

$ python3 -m pip install -r requirements.txt

### Vision Specs

Camera is 3-channeled, 960 x 1280 pixels, 8-bit per pixel.

Mushrooms endpoint returns vector of found mushrooms.

Each vector is encoded as 3 or 4 element floating-point vector (x,y,radius) or (x,y,radius,votes)

CV2 is BGR (not RGB) 

 

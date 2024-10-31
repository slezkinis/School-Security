import cv2, imutils, socket
import numpy as np
import time
import base64
import websocket
from pprint import pprint


BUFF_SIZE = 65536
ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:8000/exit/-1")
while True:
    pprint(ws.recv())
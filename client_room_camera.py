# This is client code to receive video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64
import websocket


BUFF_SIZE = 65536
ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:8000/room/camera/1_camera")
fps,st,frames_to_count,cnt = (0,0,20,0)
vid = cv2.VideoCapture(1) #  replace 'rocket.mp4' with 0 for webcam
try:
	while True:
		while(vid.isOpened()):
			WIDTH=400
			_,frame = vid.read()
			frame = imutils.resize(frame,width=WIDTH)
			encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
			message = base64.b64encode(buffer)
			ws.send_binary(message)
			# ws.send({"id": 1, "data": message.decode()})
			frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
			# cv2.imshow('TRANSMITTING VIDEO',frame)
			key = cv2.waitKey(1) & 0xFF
			if key == ord('q'):
				ws.close()
				break
			if cnt == frames_to_count:
				try:
					fps = round(frames_to_count/(time.time()-st))
					st=time.time()
					cnt=0
				except:
					pass
			cnt+=1
			time.sleep(0.3)
except KeyboardInterrupt:
	ws.close()
	raise KeyboardInterrupt
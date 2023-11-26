import json
import base64
import numpy as np
import cv2
import math
import random
from cvzone.HandTrackingModule import HandDetector 
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
#Variables



class VideoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("connected")
        await self.accept()
        


    # async def hand_gesture(message):
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action',None)

        if action == 'start_video':
            await self.send(text_data=json.dumps({'status':'Video streaming started.'}))
            await self.process_video_frames()
        
    
    async def process_video_frames(self):
        width , height = 1280, 720

        #Camera Setup
        cap = cv2.VideoCapture(0)
        cap.set(3,width)
        cap.set(4,height)
        small_width , small_height = 400, 300
        gestureThreshold = 500
        center_cam = 600
        buttonPressed = False
        buttonCounter = 0
        buttonDelay = 30
        annotations = []
        # Hand Detector
        detector = HandDetector(detectionCon=0.8,maxHands=1)
        while True:
            success, img = cap.read()
            # print(img)
            small_img = cv2.resize(img, (small_width, small_height))

            # Display the resized frame
            small_img = cv2.flip(small_img,1)
            cv2.imshow("Small Image", small_img)
            img = cv2.flip(img,1)
            # cv2.imshow("image",img)

            hands, img = detector.findHands(img)
            cv2.line(img , (0,gestureThreshold) , (width , gestureThreshold),(0,255,0),10)
            
            if hands and buttonPressed is False:
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                cx,cy = hand['center']
                lmList = hand["lmList"]
                #tip of the index 
                #constrint values for easier drawing
                indexFinger = lmList[8][0], lmList[8][1]
                # xVal = int(np.interp(lmList[8][0],[width//2],[0,width]))
                # yVal = int(np.interp(lmList[8][1], [150,height-150],[0,height]))
                # indexFinger = xVal,yVal
                #checking for the gestures
                if cy <= gestureThreshold:

                    #Gesture 1 - Left
                    if fingers == [1,0,0,0,0]:
                        # index 4 corresponds to the tip of the thumb
                        thumb_tip = hand["lmList"][4]
                        x,y = thumb_tip[1], thumb_tip[2]
                        print("thumb_tip",x,y)
                        angle_rad = math.atan2(y-cy , x-cx)
                        angle_deg = math.degrees(angle_rad)
                        print(angle_deg)


                        buttonPressed = True
                        # instead of this call the consumer thing and send a response 
                        await self.send(text_data=json.dumps({'prediction':"left"}))
                        print("left")
                    #Gesture 2 - Right
                    elif fingers == [0,0,0,0,1]:
                        buttonPressed = True
                        #instead of this call send the response
                        await self.send(text_data=json.dumps({'prediction':"right"}))
                        print("Right")

                    #Gstrue 3 and 4 - seek_left || seek_right  
                    elif fingers == [1,1,1,1,1]:
                        if cx <= center_cam:
                            # fast_backward
                            buttonPressed = True
                            await self.send(text_data=json.dumps({'prediction':"seek_left"}))
                            print("seek_left")
                        else:
                            # fast_forward 
                            buttonPressed = True
                            await self.send(text_data=json.dumps({'prediction':"seek_right"}))
                            print("seek_right")
                    
                    #Tracker start
                if fingers == [0,1,1,0,0]:
                        await self.send(text_data=json.dumps({"prediction" : "start_drwaing"}))

                #Drawing 
                if fingers == [0,1,0,0,0] and indexFinger[0] >= 640 and indexFinger[1] <= 400:
                    indexFinger = indexFinger[0]-640 , 400 - indexFinger[1]
                    print(indexFinger)
                    await self.send(text_data=json.dumps({"prediction" : "draw", "points": indexFinger}))
                    annotations.append(indexFinger)
            #Button Pressed Iteration 
            if buttonPressed:
                buttonCounter +=1
                if buttonCounter > buttonDelay:
                    buttonCounter = 0 
                    buttonPressed = False

            # for annotation in annotations :
            #     print("hello")

            # print(hands)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            await asyncio.sleep(0.0001)
        cap.release()
        cv2.destroyAllWindows()

import cv2 as cv
import numpy as np
from tracker import *
import random
import numpy as np
from flask import jsonify


def capture(f):
    print(f)
    video = cv.VideoCapture(f)
    frames_count, fps, width, height = video.get(cv.CAP_PROP_FRAME_COUNT), video.get(cv.CAP_PROP_FPS), video.get(cv.CAP_PROP_FRAME_WIDTH), video.get(cv.CAP_PROP_FRAME_HEIGHT)
    print(frames_count, fps)

    object_detector = cv.createBackgroundSubtractorMOG2(history=100, varThreshold = 50)
    tracker = distanceTracker()

    pts= {}
    dir = {}
    col = [( random.randint(0, 255) ,random.randint(0, 255), random.randint(0, 255) ), ( random.randint(0, 255) ,random.randint(0, 255), random.randint(0, 255) ), ( random.randint(0, 255) ,random.randint(0, 255), random.randint(0, 255) ) ]


    while True:
        check, frame = video.read()
        f =0
        if not check:
            break
        if check:

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            
            mask = object_detector.apply(gray)
            
            kernel =cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
            closing = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
            opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernel)
            ero = cv.erode(opening, None, iterations=2)
            dilation = cv.dilate(ero, None, iterations=2)
            retval, bins = cv.threshold(dilation, 240, 255, cv.THRESH_BINARY)

            contours, hierarchy = cv.findContours(bins, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            detection = []
            for cnt in contours:
                area = cv.contourArea(cnt)
                if area > 50:
                    #cv.drawContours(frame, [cnt], -1, (0,0,255), 2)
                    x, y, w, h = cv.boundingRect(cnt)
                    #cv.rectangle(frame, (x,y), (x + w, y+ h), (0, 255, 0), 3)
                    detection.append([x, y, w, h])
            #print(detection)

            boxes_ids = tracker.track(detection)
            c= 0
            idx =0
            nor =0
            sou = 0
            stand = 0
            for box_id in boxes_ids:
                x, y, w, h, id = box_id
                cx = (x + x + w)//2
                cy = (y + y + h)//2
                if id not in pts.keys():
                    pts[id] = []
                pts[id].append((cx,cy))
                c = c+1
                dir[id] = 'Unknown'
                cv.line(frame, pts[id][0], pts[id][-1], col[int(id%3)] , 2)

                if len(pts[id]) >= 5:
                    dX = pts[id][-4][0] - pts[id][-1][0]
                    dY = pts[id][-4][1] - pts[id][-1][1]
                    dirY =  ""
                    dirX = ""
                    if np.abs(dY) > 2:
                        dirY = "North" if np.sign(dY) == 1 else "South"
                    elif np.abs(dX) > 2:
                        dirX = "East" if np.sign(dY) == 1 else "West"
                    if dirY != "":
                        dir[id] = dirY
                    # otherwise, only one direction is non-empty
                    else:
                        dir[id] = dirX
                    

                cv.putText(frame, str(dir[id]), (x, y - 15), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                idx = idx+ 1
                if dir[id] == 'North':
                    nor = nor + 1
                elif dir[id] == 'South':
                    sou = sou + 1
                elif dir[id] == 'East' or dir[id] == 'West':
                    pass
                else:
                    stand = stand + 1

            cv.putText(frame, 'Total no. of vehicles not moving in frame:'+str(stand), (100, 20), cv.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1 )
            cv.putText(frame, 'Total no. of vehicles moving in frame:'+str(idx-stand), (100, 40), cv.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1 )
            cv.putText(frame, 'Current no. of vehicles moving North:'+str(nor), (100, 60), cv.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1 )
            cv.putText(frame, 'Current no. of vehicles moving South:'+str(sou), (100, 80), cv.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1 )
            cv.putText(frame, 'Press q to exit and p to pause the video', (100, 100), cv.FONT_HERSHEY_SIMPLEX, .5, (0,0,255), 1 )
            
            cv.imshow('frame', frame)
            #cv.imshow('mask', mask)
            #cv.imshow('dilation', dilation)
            #cv.imshow('retval', bins)
            f=f+1


            key = cv.waitKey(1)
            if key == ord('q'):
                break
            if key == ord('p'):
                cv.waitKey(-1)

    nor =0
    sou =0  
    dir = {key:val for key, val in dir.items() if val != 'Unknown'}
    #print(dir) 
    for i in dir.values():
        if i == 'North':
            nor = nor+1
        elif i == 'South':
            sou = sou +1            
    dn = nor/int(fps)
    ds = sou/int(fps)
    dv = len(dir)/int(fps)
    r = {'dn': dn,
         'ds': ds,
         'dv': dv,
         'fps': fps,
        }
    video.release()
    cv.destroyAllWindows()
    return jsonify(r)






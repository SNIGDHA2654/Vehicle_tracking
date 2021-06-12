import math
from collections import deque
import cv2 as cv

class distanceTracker:
    def __init__(self):
        self.center = {}
        self.id = 0
        self.pts = {}
    
    def track(self, obj):
        obj_id = []

        for cord in obj:
            x, y, w, h = cord
            cx = (x + x + w)//2
            cy = (y + y + h)//2

            sameObject = False
            
            for id, pt in self.center.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 25:
                    self.center[id] = (cx, cy)

                    #print(self.center)
                    obj_id.append([x, y, w, h, id])
                    sameObject = True
                    break
            
            if sameObject is False:
                self.center[self.id] = (cx, cy)
                obj_id.append([x, y, w, h, self.id])
                self.id += 1

        new_center_points = {}
        for obj in obj_id:
             _, _, _, _, object_id = obj
             center = self.center[object_id]
             new_center_points[object_id] = center

        self.center = new_center_points.copy()
        return obj_id

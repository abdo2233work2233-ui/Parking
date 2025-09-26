import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
import os


# Load the YOLOv8 model
model = YOLO("yolov8n.pt")

# Export the model to TorchScript format


def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:  
        colorsBGR = [x, y]
        print(colorsBGR)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

# Replace this with the path to your image directory
image_directory = 'images2'
image_files = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

# Define your areas
areas = [

[(128,214),(88,254),(197,256),(231,214)],

[(286,214),(260,267),(377,256),(386,217)],

[(449,214),(429,270),(609,256),(580,214)],

[(625,214),(631,259),(793,256),(726,214)],

[(771,214),(822,251),(1005,250),(929,214)]
]


Frames_Num = []
Predict_Num_Of_Spaces = []

for image_file in image_files:
    frame = cv2.imread(image_file)
    frame = cv2.resize(frame, (1020, 500))

    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")
    
    lists = [[] for _ in range(len(areas))]
    fps = len(Frames_Num) + 1
    
    for index, row in px.iterrows():
        x1, y1, x2, y2, _, d = map(int, row[:6])
        c = class_list[d]
        
        if 'car' in c:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            for i, area in enumerate(areas):
                result = cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False)
                if result >= 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                    lists[i].append(c)
                    cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)


    occupied_spaces = sum(len(l) for l in lists)
    space = 5 - occupied_spaces
    
    Predict_Num_Of_Spaces.append(space)
    Frames_Num.append(fps)
    
    for i, (area, list) in enumerate(zip(areas, lists), start=1):
        color = (0, 0, 255) if len(list) == 1 else (0, 255, 0)
        cv2.polylines(frame, [np.array(area, np.int32)], True, color, 2)
        cv2.putText(frame, str(i), (area[0][0] + 50, area[0][1] + 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

    cv2.putText(frame,'Number of cars in parking =' + str(5-space),(50, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
 
    cv2.imshow("RGB", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()


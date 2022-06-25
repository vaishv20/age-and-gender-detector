
import cv2
import math
import argparse

from textblob import Blobber
def highlightFace(Net,frame,conf_threshold = 0.7):
    Frameopencvdnn = Frame.copy()
    Frameheight = Frameopencvdnn.shape[0]
    Framewidth = Frameopencvdnn.shape[1]
    blob = cv2.dnn.blobFromImage(Frameopencvdnn,1.0,(300,300),[104,117,123],True,False)
    Net.setInput(blob)
    detection = Net.forward()
    faceboxes = []
    for i in range(detection.shape[2]):
        confidence = detection[0,0,i,2]
        if confidence>conf_threshold:
            x1 = int(detection[0,0,i,3]*Framewidth)
            x2 =int(detection[0,0,i,5]*Framewidth)
            y1 =int(detection[0,0,i,4]*Frameheight)
            y2 = int(detection[0,0,i,6]*Frameheight)
            faceboxes.append([x1,y1,x2,y2])
            cv2.rectangle(Frameopencvdnn,(x1,y1),(x2,y2),(0,255,0),int(round(Frameheight/150)),8)
    return Frameopencvdnn,faceboxes            
parser = argparse.ArgumentParser()
parser.add_argument('--image')
args = parser.parse_args()
faceproto = "opencv_face_detector.pbtxt"
facemodule = "opencv_face_detector_uint8.pb"
ageproto = "age_deploy.prototxt"
agemodule = "age_net.caffemodel"
genderproto = "gender_deploy.prototxt"
gendermodule = "gender_net.caffemodel"
MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList=['Male','Female']
facenet = cv2.dnn.readNet(facemodule,faceproto)
agenet = cv2.dnn.readNet(agemodule,ageproto)
gendernet = cv2.dnn.readNet(gendermodule,genderproto)
video = cv2.VideoCapture(args.image if args.image else 0)
padding = 20
while cv2.waitKey(1)<0:
    hasFrame, Frame = video.read()
    if not hasFrame:
        cv2.waitKey()
        break
    resultimg,faceboxes = highlightFace(facenet,Frame)
    if not faceboxes:
        print("No face detected")
    for facebox in faceboxes:
        face = Frame[max(0,facebox[1]-padding):min(facebox[3]+padding,Frame.shape[0]-1),max(0,facebox[0]-padding):min(facebox[2]+padding,Frame.shape[1]-1)]
        blob = cv2.dnn.blobFromImage(face,1.0,(227,227),MODEL_MEAN_VALUES,swapRB = False)
        gendernet.setInput(blob)    
        genderpredict = gendernet.forward()
        gender = genderList[genderpredict[0].argmax()]
        print(F'gendercolon{gender}')
        agenet.setInput(blob)
        agepredict = agenet.forward()
        age = ageList[agepredict[0].argmax()]
        print(F'agecolon{age}')
        cv2.putText(resultimg,F'{gender},{age}',(facebox[0],facebox[1]-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2,cv2.LINE_AA)
        cv2.imshow('age and gender', resultimg)

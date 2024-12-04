import cv2
import pickle
import cvzone
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore    

cred = credentials.Certificate('keys.json')
firebase_admin.initialize_app(cred, {
    'projectId': "-",
})
db = firestore.client()

# Video feed
cap = cv2.VideoCapture('video.MOV')

with open('TablePos', 'rb') as f:
    posList = pickle.load(f)

width, height = 120, 200

flag = [0, 0, 0, 0]
realflag = [0, 0, 0, 0]
flagtime = [0, 0, 0, 0]

def senddata():
    doc_ref = db.collection(u'users').document(u'828')
    doc_ref.set({
        u'1': realflag[0],
        u'2': realflag[1],
        u'3': realflag[2],
        u'4': realflag[3],
    })

senddata()

def flagchange(i, count):
    if count < 100:

        if flag[i] == 1:
            flagtime[i] = videomsec
            flag[i] = 0

        if realflag[i] == 1 and (videomsec - flagtime[i]) / 1000 > 5:
            realflag[i] = 0
            # print("좌석 상태", i + 1, realflag[i])
            senddata()


    else:
        if flag[i] == 0:
            flagtime[i] = videomsec
            flag[i] = 1

        if realflag[i] == 0 and (videomsec - flagtime[i]) / 1000 > 5:
            realflag[i] = 1
            # print("좌석 상태", i + 1, realflag[i])
            senddata()

def checkParkingSpace(imgPro):

    for i in range(4):
        x, y = posList[i]


        imgCrop = imgPro[y:y + height, x:x + width]
        #cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)

        flagchange(i, count)

        if flag[i] == 1:
            color = (0, 0, 255)
            thickness = 2

        else:
            color = (0, 255, 0)
            thickness = 5




        cv2.rectangle(img, posList[i], (posList[i][0] + width, posList[i][1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)


fps = cap.get(cv2.CAP_PROP_FPS)
while True:


    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    img = cv2.resize(img, dsize=(1280, 720))
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 회색으로 바꾸기
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # 회색으로 바꾼걸 가우시안블러로 노이즈제거하기
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # 적응형 이진화
                                         cv2.THRESH_BINARY_INV, 25, 8)
    imgMedian = cv2.medianBlur(imgThreshold, 5)  # 소금후추 잡음 제거
    kernel = np.ones((3, 3), np.uint8)  # 행렬 1로 초기화
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)  # iteration값이 커질수록 이미지 외각 픽셀 dilate는 증가, erode는 감소

    videomsec = cap.get(cv2.CAP_PROP_POS_MSEC)


    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    if videomsec < 1000:
        for i in range(4):
            flagtime[i] = 0

    for i in range(4):
        print(i + 1, flag[i], realflag[i], int(videomsec - flagtime[i]) // 1000, end='  ')
    print(int(videomsec)//1000)

    # cv2.imshow("imgGray",imgGray)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("Imagethreshold",imgThreshold)
    # cv2.imshow("ImgMedian",imgMedian)
    # cv2. imshow("imgdilate",imgDilate)
    cv2.waitKey(int(1000/fps))

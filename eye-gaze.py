import serial
import numpy as np
import cv2, sys, requests
from matplotlib import pyplot as plt

def plot_circle(img, circle):
    img = img.copy()
    if circle == None:
        return img

    cv2.circle(img, circle[0], circle[1], (255, 0, 255), 3, cv2.LINE_AA)
    cv2.circle(img, circle[0], int(circle[1]+circle[1]*0.6), (255, 0, 255), 3, cv2.LINE_AA)
    cv2.circle(img, circle[0], 2, (0, 255, 0), 3, cv2.LINE_AA)

    return img

def inCircle(x, y, img):
    if img[y,x] == 255:
        return True
    return False

def checkcircle(img, circle):
    # accept binary image
    row = img.shape[0]
    col = img.shape[1]
    x = circle[0][0]
    y = circle[0][1]
    r = circle[1]
    area = 0
    small_intensity = 0
    big_intensity = 0

    small_circle_img = np.zeros(img.shape)
    big_circle_img = np.zeros(img.shape)
    cv2.circle(small_circle_img, (x,y), r, (255,255,255), -1, cv2.LINE_AA)
    cv2.circle(big_circle_img, (x,y), int(r+r*0.6), (255,255,255), -1, cv2.LINE_AA)

    minx = int(max(0, x-r-20))
    maxx = int(min(x+r+20, col))
    miny = int(max(0, y-20))
    maxy = int(min(y+r+20, row))

    if minx == 0 or miny == 0 or maxx == col or maxy == row:
        return False, None

    for xx in xrange(minx, maxx):
        for yy in xrange(miny, maxy):
            if inCircle(xx, yy, small_circle_img):
                area += 1
                if img[yy, xx] == 255:
                    small_intensity += 1
            if inCircle(xx, yy, big_circle_img):
                if img[yy, xx] == 255:
                    big_intensity += 1

    if small_intensity < area*0.7:
        return False, None
    intensity_diff = big_intensity - small_intensity
    if intensity_diff > area*0.40:
        return False, None

    w1 = 3.0
    w2 = 20.0
    area = float(area)
    score = w1*small_intensity/area + w2*(1.0-1.3*intensity_diff/area)

    return True, score

def get_pupil_location(img, method=1):
    pupil_location = {}

    thres_img = 255-img
    ret,thres_img = cv2.threshold(thres_img,210,255,cv2.THRESH_TOZERO)
    ret,thres_img = cv2.threshold(thres_img,127,255,cv2.THRESH_BINARY)

    pupil_location['thres_image'] = thres_img.copy()

    circles = []

    # method 1, use ori color image with houghcircle
    pupil_location['ori_image'] = img.copy()
    detected_circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 200, np.array([]), 100, 80, 20, 60)
    if detected_circles is not None:
        a, b, c = detected_circles.shape
        for i in range(b):
            c = detected_circles[0][i]
            c = ((c[0], c[1]), c[2])
            check, score = checkcircle(thres_img, c)
            if check:
                circles.append((score, c))
    # method 2, use threshold image
    pupil_location['ori_image'] = thres_img.copy()
    detected_circles = cv2.HoughCircles(thres_img, cv2.HOUGH_GRADIENT, 2, 20, np.array([]), 100, 40, 20, 60)
    if detected_circles is not None:
        a, b, c = detected_circles.shape
        for i in range(b):
            c = detected_circles[0][i]
            c = ((c[0], c[1]), c[2])
            check, score = checkcircle(thres_img, c)
            if check:
                circles.append((score, c))
    # method 3, use mser
    # pupil_location['ori_image'] = cimg.copy()
    # mser = cv2.MSER_create(5, 900, 3080, 0.25, 0.2, 200, 1.01, 0.003, 1)
    # keypoint = mser.detect(cimg)

    # for i in keypoint:
    #     c = ((int(i.pt[0]), int(i.pt[1])), int(i.size*0.75))
    #     check, score = checkcircle(thres_img, c)
    #     if check:
    #         circles.append((score, c))

    ## debug
    # dbg = thres_img.copy()
    # for c in circles:
    #     dbg = plot_circle(dbg, c[1])
    #     print "score: ", c[0]
    #     cv2.imshow('debug', dbg)
    #     x = checkcircle(thres_img, c[1])
    #     print x
    #     cv2.waitKey()

    print len(circles)
    if len(circles):
        # find best circle
        # citeria: closest % to small area, lowest intensity diff
        pupil_location['pupil'] = sorted(circles)[-1][1]
    else:
        pupil_location['pupil'] = None
    return pupil_location


frame = 0
start = cv2.getTickCount()
last_eye_close = cv2.getTickCount()
last_eye_open = cv2.getTickCount()
eye_open = False
cx, cy = 0, 0
sx, sy, sc = 0, 0, 0
url = "http://192.168.137.1:8888/out.jpg"
arduino = serial.serial_for_url("/dev/tty.HC-05-DevB", 9600)
# arduino.write()
# cap = cv2.VideoCapture("http://192.168.137.1:8081/video.mjpg", cv2.CAP_FFMPEG)

def main(img, cimg):
    pupil_location = get_pupil_location(img, method=3)

    global last_eye_close
    global last_eye_open
    global eye_open
    global cx, cy
    global sx, sy, sc

    if pupil_location['pupil'] != None:
        last_eye_open = cv2.getTickCount()
        if eye_open == False:
            # do calibration
            pupil = pupil_location['pupil']
            sx += pupil[0][0]
            sy += pupil[0][1]
            sc += 1
            print "CALIBRATING"
            print sx, sy, pupil[0][0], pupil[0][1]

    # do respond + display purpose
    # cv2.imshow('image', img)
    # cv2.moveWindow('image', 0, 0)
    cv2.imshow('detection', plot_circle(cimg, pupil_location['pupil']))
    cv2.moveWindow('detection', 600, 0)
    # cv2.imshow('ori image', pupil_location['ori_image'])
    # cv2.moveWindow('ori image', 0, 500)
    # cv2.imshow('thres image', pupil_location['thres_image'])
    # cv2.moveWindow('thres image', 600, 500)

    # calibrate for 10 sec
    sec = (cv2.getTickCount()-last_eye_close)/cv2.getTickFrequency()
    if sec > 10:
        # calibrated
        cx, cy = 1.0*sx/sc, 1.0*sy/sc
        eye_open = True

    # eye close start from 5 sec
    if (cv2.getTickCount()-last_eye_open)/cv2.getTickFrequency() > 5:
        last_eye_close = cv2.getTickCount()
        eye_open = False
        sx, sy, sc = 0, 0, 0
        x, y = 0, 0

    if eye_open and pupil_location['pupil']:
        # do command
        pupil = pupil_location['pupil']
        px, py = pupil[0][0], pupil[0][1]

        OFFSET = 50
        print cx, cy, px, py

        if py < cy - OFFSET:
            print "UP"
            arduino.write('1')
        elif py > cy + OFFSET:
            print "DOWN"
            arduino.write('4')
        elif px < cx - OFFSET:
            print "LEFT"
            arduino.write('3')
        elif px > cx + OFFSET:
            print "RIGHT"
            arduino.write('2')

        else:
            print "IDLE"
            arduino.write('0  ')


# r = requests.get('http://192.168.137.1:8081/video.mjpg', stream=True)
# if(r.status_code == 200):
#     bytes = bytes()
#     for chunk in r.iter_content(chunk_size=1024):
#         bytes += chunk
#         a = bytes.find(b'\xff\xd8')
#         b = bytes.find(b'\xff\xd9')
#         if a != -1 and b != -1:
#             jpg = bytes[a:b+2]
#             bytes = bytes[b+2:]
#             img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), 0)
#             cimg = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), -1)
#             # main(img, cimg)
#             if cv2.waitKey(1) == 27:
#                 exit(0)

#             # fps statistic
#             frame += 1
#             cur = cv2.getTickCount()
#             sec = (cur-start)/cv2.getTickFrequency()
#             print "fps: ", frame/sec
# else:
#     print("Received unexpected status code {}".format(r.status_code))

# static image debug
# for i in range(10):
#     img = cv2.imread("sample-img/temp/out_0" + str(i)+ ".jpg", 0)
#     cimg = cv2.imread("sample-img/temp/out_0" + str(i)+ ".jpg")

#     main(img, cimg)
#     cv2.waitKey()
# exit()

while True:
    # get poll img
    r = requests.get(url)

    img_array = np.array(bytearray(r.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, 0)
    cimg = cv2.imdecode(img_array, -1)

    main(img, cimg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # fps statistic
    frame += 1
    cur = cv2.getTickCount()
    sec = (cur-start)/cv2.getTickFrequency()
    print "fps: ", frame/sec

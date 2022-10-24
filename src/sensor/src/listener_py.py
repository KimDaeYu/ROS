#!/usr/bin/env python
#-*- coding:utf-8 -*- 

import sys, time

import rospy
from sensor.msg import CompressedImage	# 패키지의 메시지 파일

import cv2
import numpy as np


VERBOSE=False

pub = rospy.Publisher("/output/compressed/",
                    CompressedImage)
# 퍼블리셔 노드로부터 토픽을 받아들이는 콜백 함수
def callback(ros_data):
    global pub

    if VERBOSE:
        print('received image of type: "%s"' % ros_data.format)

    np_arr = np.fromstring(ros_data.data, np.uint8)
    image_np = cv2.imdecode(np_arr, cv2.CV_LOAD_IMAGE_COLOR)

    method = "GridFAST"
    feat_det = cv2.FeatureDetector_create(method)
    time1 = time.time()

    featPoints = feat_det.detect(cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY))

    time2 = time.time()

    if VERBOSE:
        print('%s detector found: %s points in: %s sec.'%(method,
        len(featPoints),time2-time1))

    for featpoint in featPoints:
        x,y = featpoint.pt
        cv2.circle(image_np,(int(x),int(y)), 3, (0,0,255), -1)

    cv2.imshow('cv_img', image_np)
    cv2.waitKey(2)

    #### Create CompressedIamge ####
    msg = CompressedImage()
    msg.header.stamp = rospy.Time.now()
    msg.format = "jpeg"
    msg.data = np.array(cv2.imencode('.jpg', image_np)[1]).tostring()
    # Publish new image
    pub.publish(msg)


def main():
    # 노드 초기화. 이름은 listener
    rospy.init_node('listener', anonymous=True)

    # 특정 토픽(chatter)를 callback이라는 이름의 함수로 받아들이며, 메시지 타입은 test_msg
    rospy.Subscriber("chatter", CompressedImage, callback)

    rospy.spin()

if __name__ == '__main__':
    main()
#! /usr/bin/python2

import time
import sys
import os
import logging

import RPi.GPIO as GPIO
from picamera import PiCamera
from datetime import datetime

from hx711 import HX711
from classifier import Classifier
import food_logger


logging.basicConfig(filename="main.log", level=logging.DEBUG)

IMAGES_FOLDER = "images"
camera = PiCamera()
classfier = Classifier(
    "converted_tflite/model_unquant.tflite", "converted_tflite/labels.txt"
)

if not os.path.exists(IMAGES_FOLDER):
    os.mkdir(IMAGES_FOLDER)


def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")


def capture():
    img_name = int(time.time())
    img_path = f"images/{img_name}.jpg"
    camera.capture(img_path)
    return img_path


referenceUnit = 346
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

print("Tare done! Add weight now...")


while True:
    try:
        val_A = hx.get_weight(5)
        counter = 0
        # print(val_A)
        # logging.info(val_A)

        while val_A > 10:
            counter += 1
            img_path = capture()
            label = classfier.infer(img_path)
            logging.info(f"{label} : {int(val_A)}gm")

            if counter == 3 and label is not None:
                food_logger.log(label, val_A)

            print(val_A)
            hx.power_down()

            hx.power_up()
            time.sleep(0.2)
            val_A = hx.get_weight(5)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()

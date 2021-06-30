#! /usr/bin/python2
import RPi.GPIO as GPIO
from hx711 import HX711

from picamera import PiCamera
import os
import time

from classifier import Classifier
import food_logger


camera = PiCamera()
classifier = Classifier(
    "converted_tflite/model_unquant.tflite", "converted_tflite/labels.txt"
)

IMAGES_FOLDER = "images"
if not os.path.exists(IMAGES_FOLDER):
    os.mkdir(IMAGES_FOLDER)


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
        value = hx.get_weight()
        counter = 0
        print(value)

        while value > 10:
            img_path = capture()
            label = classifier.infer(img_path)
            print(f"{label} : {int(value)}gm")

            counter += 1
            if counter == 3:
                food_logger.log(label, value)

            time.sleep(0.2)
            value = hx.get_weight()

    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()

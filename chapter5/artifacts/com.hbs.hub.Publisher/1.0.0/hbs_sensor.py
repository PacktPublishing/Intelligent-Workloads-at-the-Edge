# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import random
import numpy as np
from time import sleep, time
from random import gauss


class DummySensor(object):
    def __init__(self, mean=25, variance=1):
        self.mu = mean
        self.sigma = variance
        
    def read_value(self):
        
        message = {}
        
        device_list = ['hvac', 'refrigerator', 'washingmachine']
        device_name = random.choice(device_list)
        
        if device_name == 'hvac' :
            message['device_id'] = "1"
            message['timestamp'] = float("%.4f" % (time()))
            message['device_name'] = device_name
            message['temperature'] = round(random.uniform(10.0, 99.0), 2)
            message['humidity'] = round(random.uniform(10.0, 99.0), 2)
        elif device_name == 'washingmachine' :
            message['device_id'] = "2"
            message['timestamp'] = float("%.4f" % (time()))
            message['device_name'] = device_name
            message['duty_cycles'] = round(random.uniform(10.0, 99.0), 2)
        else :
            message['device_id'] = "3"
            message['timestamp'] = float("%.4f" % (time()))
            message['device_name'] = device_name
            message['vibration'] = round(random.uniform(100.0, 999.0), 2)
        
        return message


if __name__ == '__main__':
    sensor = DummySensor()
    print(sensor.read_value())

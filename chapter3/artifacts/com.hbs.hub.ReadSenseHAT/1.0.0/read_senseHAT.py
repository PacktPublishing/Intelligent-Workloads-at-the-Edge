#!/usr/bin/env python

"""read_senseHAT.py: read sensor values and publish them on IPC

   Read sensor values from the Sense HAT expansion module
   installed on a Raspberry Pi. Publish measured values
   to a local topic using IoT Greengrass IPC.
"""

__author__ = "Ryan Burke"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Development"

import sys, time, logging
from sense_hat import SenseHat
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    PublishToTopicRequest,
    PublishMessage,
    JsonMessage
)

# timeout, in seconds, to expire attempted publish
TIMEOUT = 10

# sleep timer, in seconds, until next read and publish
DELAY = 10

# init logger
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def build_message():
    r"""Builds a dictionary of the message to publish.

    Reads temperature and humidity values from SenseHAT.
    Message has timestamp, values, and device_id.
    device_id is assumed to be 'hvac' in this scenario.

    Returns
    -------
    message : dict
    """
    sense = SenseHat()
    message = {}
    message['timestamp'] = float("%.4f" % (time.time()))
    message['device_id'] = 'hvac'
    message['temperature'] = sense.get_temperature()
    message['humidity'] = sense.get_humidity()

    return message

def publish_message(ipc_client, topic, message):
    r"""Publish a message to a local topic over IPC.

    Parameters
    ----------
    ipc_client : object
        An instance of a connected awsiot.greengrasscoreipc client
    topic : string
        The local topic upon which to publish the message.
    message : dict
        Dictionary of key-value pairs to publish on the topic.
    """
    publish_message = PublishMessage()
    publish_message.json_message = JsonMessage()
    publish_message.json_message.message = message
    request = PublishToTopicRequest()
    request.topic = topic
    request.publish_message = publish_message
    operation = ipc_client.new_publish_to_topic()
    operation.activate(request)
    future = operation.get_response()
    try:
        future.result(TIMEOUT)
        logger.info('published message, payload is: %s', request.publish_message)
    except Exception as e:
        logger.error('failed message publish: %s', e)

def main():
    r"""Endlessly reads values from SenseHAT and publish on IPC.

    Parameters
    ----------
    sys.argv[1] : string
        Optional. Overrides the default local topic used in
        local IPC message publishing.
    sys.argv[2] : any
        Optional. Any truthy value will enable test_mode,
        skipping any use of the IoT Greengrass SDK.
    """
    topic = 'dt/local/sensor/hvac' if len(sys.argv) < 2 else sys.argv[1]
    test_mode = False if len(sys.argv) < 3 else sys.argv[2]
    if test_mode:
        logger.info('[test_mode] truthy argument passed in sys.argv[2], test_mode enabled')
    else:
        ipc_client = awsiot.greengrasscoreipc.connect()
    while True:
        message = build_message()
        if test_mode:
            logger.info('[test_mode] topic is: %s', topic)
            logger.info('[test_mode] payload is: %s', message)
        else:
            publish_message(ipc_client, topic, message)
        time.sleep(DELAY)

if __name__ == "__main__":
    main()

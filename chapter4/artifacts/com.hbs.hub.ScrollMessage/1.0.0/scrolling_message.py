#!/usr/bin/env python

"""scrolling_message.py: write received messages to SenseHAT

   Subscribes to an IoT Core topic and writes message 
   contents to the SenseHAT using the 8x8 LED matrix.
"""

__author__ = "Ryan Burke"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Development"

import sys, time, logging, traceback
from sense_hat import SenseHat
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    SubscribeToIoTCoreRequest
)

# timeout, in seconds, to expire attempted subscribe
TIMEOUT = 10

# sleep timer, in seconds, to keep process open
DELAY = 10

# MQTT quality of service (QoS). Use QoS0
qos = QOS.AT_MOST_ONCE

# init logger
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message = str(event.message.payload, "utf-8")
            topic_name = event.message.topic_name
            logger.info('message received on topic %s. message: %s', topic_name, message)
            scroll_message(message)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass

def subscribe_to_topic(topic):
    logger.info('subscribe to IoT Core topic')
    ipc_client = awsiot.greengrasscoreipc.connect()
    request = SubscribeToIoTCoreRequest()
    request.topic_name = topic
    request.qos = qos
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_iot_core(handler) 
    future = operation.activate(request)
    future.result(TIMEOUT)
    logger.info('subscribed to IoT Core topic %s', topic)

def scroll_message(message):
    sense = SenseHat()
    sense.show_message(message)

def main():
    r"""Subscribe to IPC and scroll messages received.

    Parameters
    ----------
    sys.argv[1] : string
        Optional. Overrides the default local topic used in
        local IPC message subscribing.
    sys.argv[2] : any
        Optional. Any truthy value will enable test_mode,
        skipping any use of the IoT Greengrass SDK.
    """
    topic = 'ml/dlr/image-classification' if len(sys.argv) < 2 else sys.argv[1]
    test_mode = False if len(sys.argv) < 3 else sys.argv[2]
    if test_mode:
        logger.info('[test_mode] truthy argument passed in sys.argv[2], test_mode enabled')
    else:
        subscribe_to_topic(topic)
    while True:
        if test_mode:
            message = '[test] cat detected'
            logger.info('[test_mode] topic is: %s', topic)
            logger.info('[test_mode] sample payload is: %s', message)
            scroll_message(message)
        time.sleep(DELAY)

if __name__ == "__main__":
    main()

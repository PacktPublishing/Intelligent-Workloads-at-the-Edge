#!/usr/bin/env python

"""log_measurements.py: receive measurements and log them

   Subscribes to a local IPC topic, receives messages and
   writes them to the logger.
   Messages should include values for temperature and
   humidity.
   Use this component when deploying book examples without
   a SenseHAT device.
"""

__author__ = "Ryan Burke"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Development"

import logging, sys, time, traceback
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage
)

# timeout, in seconds, to expire attempted subscribe
TIMEOUT = 10

# sleep timer, in seconds, to keep process open
DELAY = 10

# init logger
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class SenseHat:
  r"""Mock class representing the SenseHAT device

  Defines one of the same methods as the actual SenseHAT library.
  Method simply logs messages that would normally be scrolled on the LED matrix.
  """
  @staticmethod
  def show_message(msg):
    logger.info('[writing to SenseHAT LED matrix] %s', msg)

class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message = event.json_message.message
            logger.info('message received! %s', message)
            scroll_message('t: ' + str("%.2f" % message['temperature']))
            scroll_message('h: ' + str("%.2f" % message['humidity']))
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass

def build_message():
    r"""Builds a dictionary of a sample message.

    Only used in test_mode to simulate a received message.
    Message has timestamp, values, and device_id.
    device_id is assumed to be 'hvac' in this scenario.

    Returns
    -------
    message : dict
    """
    message = {}
    message['timestamp'] = float("%.4f" % (time.time()))
    message['device_id'] = 'hvac'
    message['temperature'] = 40
    message['humidity'] = 25

    return message

def subscribe_to_topic(topic):
    logger.info('connect to ipc')
    ipc_client = awsiot.greengrasscoreipc.connect()
    request = SubscribeToTopicRequest()
    request.topic = topic
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_topic(handler) 
    future = operation.activate(request)
    future.result(TIMEOUT)
    logger.info('subscribed to topic %s', topic)

def scroll_message(message):
    sense = SenseHat()
    sense.show_message(message)

def main():
    r"""Subscribe to IPC and scroll measurements received.

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
        subscribe_to_topic(topic)
    while True:
        logger.info('tick')
        if test_mode:
            message = build_message()
            logger.info('[test_mode] topic is: %s', topic)
            logger.info('[test_mode] sample payload is: %s', message)
            scroll_message('t: ' + str(message['temperature']))
            scroll_message('h: ' + str(message['humidity']))
        time.sleep(DELAY)

if __name__ == "__main__":
    main()

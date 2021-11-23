# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import argparse
import logging
import time
import datetime
import json
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    PublishToTopicRequest,
    PublishMessage,
    JsonMessage
)
from hbs_sensor import DummySensor

parser = argparse.ArgumentParser()
parser.add_argument("--pub-topic", required=True)
parser.add_argument("--log-level", choices={'critical', 'error', 'warning', 'info', 'debug'}, default='info')
args = parser.parse_args()

logger = logging.getLogger()

levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
level = levels.get(args.log_level)
logging.basicConfig(level=level)

TIMEOUT = 10
ipc_client = awsiot.greengrasscoreipc.connect()
sensor = DummySensor()


while True:

    message = sensor.read_value()
    message_json = json.dumps(message).encode('utf-8')

    request = PublishToTopicRequest()
    request.topic = args.pub_topic
    publish_message = PublishMessage()
    publish_message.json_message = JsonMessage()
    publish_message.json_message.message = message
    request.publish_message = publish_message
    operation = ipc_client.new_publish_to_topic()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)

    print("publish")
    time.sleep(5)

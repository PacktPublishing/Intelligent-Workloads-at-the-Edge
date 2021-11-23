import argparse
import os
import json
import logging
import time
import traceback
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    QOS,
    PublishToIoTCoreRequest,
    PublishMessage,
    JsonMessage
)
from stream_manager import (
    StreamManagerClient,
    ReadMessagesOptions,
    NotEnoughMessagesException,
    MessageStreamDefinition,
    StrategyOnFull,
    ExportDefinition,
    KinesisConfig,
    InvalidRequestException,
    StreamManagerException,
    Persistence
)

TIMEOUT = 10

parser = argparse.ArgumentParser()
parser.add_argument("--sub-topic", required=True)
parser.add_argument("--kinesis-stream", required=True)
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


ipc_client = awsiot.greengrasscoreipc.connect()

class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()
        self.message_string = None
    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:

            message_string = event.json_message.message
            stream_data(message_string)

        except:
            traceback.print_exc()
        
    def on_stream_error(self, error: Exception) -> bool:
        return True

    def on_stream_closed(self) -> None:
        pass
    
def stream_data(message_json):
    
    message_json_string = json.dumps(message_json)
    stream_name = "local_stream"
    kinesis_stream = args.kinesis_stream
    iotclient = StreamManagerClient()
    sequence_number = 0 
    try:
        # The LocalDataStream is low priority source for incoming sensor data and
        # aggregator function. 
        try:   
            iotclient.delete_message_stream(stream_name=stream_name)
        except Exception as e:
            logger.error(f"Error deleting message stream: {e}")
            pass
        
        # logger.info("Creating message stream")

        iotclient.create_message_stream(
            MessageStreamDefinition(
                name=stream_name,  # Required.
                max_size=268435456,  # Default is 256 MB.
                stream_segment_size=16777216,  # Default is 16 MB.
                time_to_live_millis=None,  # By default, no TTL is enabled.
                strategy_on_full=StrategyOnFull.OverwriteOldestData,  # Required.
                persistence=Persistence.File,  # Default is File.
                flush_on_write=False,  # Default is false.
                export_definition=ExportDefinition(
                    kinesis=[
                        KinesisConfig(
                            identifier="KinesisExport",
                            kinesis_stream_name=kinesis_stream,
                            batch_size=1,
                            batch_interval_millis=60000,
                            priority=1
                            )
                        ]
                )
            )
        )

        #logger.info("Appending message stream")

        sequence_number = iotclient.append_message(stream_name, message_json_string.encode("utf-8"))

    except StreamManagerException as e:
        logger.error(f"Error creating message stream: {e}")
        pass
    except Exception as e:
        logger.error(f"General exception error: {e}")
        pass


def setup_subscription():
    request = SubscribeToTopicRequest()
    request.topic = args.sub_topic
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_topic(handler) 
    future = operation.activate(request)
    future.result(TIMEOUT)
    return operation


def main() -> None:
    """Code to execute from script"""

    logger.info(f"Arguments: {args}")
    subscribe_operation = setup_subscription()

    while True:
        # Keep app open and running

        time.sleep(1)
        
    subscribe_operation.close()


if __name__ == "__main__":
    main()
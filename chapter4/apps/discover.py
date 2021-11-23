#!/usr/bin/env python

"""discover.py: discover a nearby Greengrass core and exchange messages with it

   Uses the Greengrass auto discovery feature to locate
   a nearby Greengrass core device, connect to it,
   then exchange MQTT messages with the cloud using
   the core device as a proxy. 
   Requires the device running this program to have
   a public internet connection to use discovery.
"""

__author__ = "Ryan Burke"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Development"

import argparse
from datetime import datetime
import json
import random
import time
import uuid

from concurrent.futures import Future
from awscrt import io
from awscrt.io import LogLevel
from awscrt.mqtt import Connection, Client, QoS
from awsiot.greengrass_discovery import DiscoveryClient, DiscoverResponse
from awsiot import mqtt_connection_builder

# constants
CERT_FILENAME = 'certificate.pem'
KEY_FILENAME = 'private.pem'
ROOTCA_FILENAME = 'rootca.pem'
THING_NAME = 'localdevice'
DEFAULT_TOPIC = 'dt/{}/heartbeat'.format(THING_NAME)
SHADOW_TOPIC = '$aws/things/{}/shadow/update'.format(THING_NAME)
SHADOW_ACCEPTED_TOPIC = '$aws/things/{}/shadow/update/accepted'.format(THING_NAME)

# optional command line arguments
# you can skip these when using the defaults defined in chapter4
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--root-ca', action='store', dest='root_ca_path', default=ROOTCA_FILENAME, help='Root CA file path')
parser.add_argument('-c', '--cert', action='store', dest='certificate_path', default=CERT_FILENAME, help='Certificate file path')
parser.add_argument('-k', '--key', action='store', dest='private_key_path', default=KEY_FILENAME, help='Private key file path')
parser.add_argument('-n', '--thing-name', action='store', dest='thing_name', default=THING_NAME, help='Targeted thing name')
parser.add_argument('--region', action='store', dest='region', default='us-west-2')
parser.add_argument('--print-discover-resp-only', action='store_true', dest='print_discover_resp_only', default=False)
parser.add_argument('-v', '--verbosity', choices=[x.name for x in LogLevel], default=LogLevel.NoLogs.name,
                    help='Logging level')

args = parser.parse_args()

io.init_logging(getattr(LogLevel, args.verbosity), 'stderr')

event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

tls_options = io.TlsContextOptions.create_client_with_mtls_from_path(args.certificate_path, args.private_key_path)
if args.root_ca_path:
    tls_options.override_default_trust_store_from_path(None, args.root_ca_path)
tls_context = io.ClientTlsContext(tls_options)

socket_options = io.SocketOptions()

print('Performing greengrass discovery...')
discovery_client = DiscoveryClient(client_bootstrap, socket_options, tls_context, args.region)
resp_future = discovery_client.discover(args.thing_name)
discover_response = resp_future.result()

print(discover_response)
if args.print_discover_resp_only:
    exit(0)


def on_connection_interupted(connection, error, **kwargs):
    print('connection interrupted with error {}'.format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print('connection resumed with return code {}, session present {}'.format(return_code, session_present))


# Try IoT endpoints returned by Greengrass discovery API until we find one that works
def try_iot_endpoints():
    for gg_group in discover_response.gg_groups:
        for gg_core in gg_group.cores:
            for connectivity_info in gg_core.connectivity:
                try:
                    print('Trying core {} at host {} port {}'.format(gg_core.thing_arn, connectivity_info.host_address, connectivity_info.port))
                    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                        endpoint=connectivity_info.host_address,
                        port=connectivity_info.port,
                        cert_filepath=args.certificate_path,
                        pri_key_filepath=args.private_key_path,
                        client_bootstrap=client_bootstrap,
                        ca_bytes=gg_group.certificate_authorities[0].encode('utf-8'),
                        on_connection_interrupted=on_connection_interupted,
                        on_connection_resumed=on_connection_resumed,
                        client_id=args.thing_name,
                        clean_session=False,
                        keep_alive_secs=30)

                    connect_future = mqtt_connection.connect()
                    connect_future.result()
                    print('Connected!')
                    return mqtt_connection

                except Exception as e:
                    print('Connection failed with exception {}'.format(e))
                    continue

    exit('All connection attempts failed')

mqtt_connection = try_iot_endpoints()

def on_receive(topic, payload, dup, qos, retain, **kwargs):
    print('Publish received on topic {}'.format(topic))
    print(payload)

subscribe_future, _ = mqtt_connection.subscribe(SHADOW_ACCEPTED_TOPIC, QoS.AT_MOST_ONCE, on_receive)
subscribe_result = subscribe_future.result()

# loop endlessly and publish messages to the shadow and heartbeat topics
while True:
    message = {
      'timestamp': datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
    }
    shadow_message = {
      'state': {
        'reported': {
          'temperature': random.gauss(35, 10)
        }
      }
    }

    pub_future, _ = mqtt_connection.publish(DEFAULT_TOPIC, json.dumps(message), QoS.AT_MOST_ONCE)
    pub_future.result()
    print('Published topic {}: {}\n'.format(DEFAULT_TOPIC, message))

    pub_future, _ = mqtt_connection.publish(SHADOW_TOPIC, json.dumps(shadow_message), QoS.AT_MOST_ONCE)
    pub_future.result()
    print('Published topic {}: {}\n'.format(SHADOW_TOPIC, shadow_message))

    time.sleep(5)

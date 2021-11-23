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

import json
import io
import urllib.request
import boto3

# constants. make sure these match what's in discover.py
CORE_NAME = 'hbshub001'
CERT_FILENAME = 'certificate.pem'
KEY_FILENAME = 'private.pem'
ROOTCA_FILENAME = 'rootca.pem'
ROOTCA_URL = 'https://www.amazontrust.com/repository/AmazonRootCA1.pem'
THING_NAME = 'localdevice'
IOT_POLICY_NAME = '{}-policy'.format(THING_NAME)
IOT_POLICY_DOC = {
  'Version': '2012-10-17',
  'Statement': [
      {
          'Effect': 'Allow',
          'Action': [
              'iot:Publish',
              'iot:Receive'
          ],
          'Resource': [
              'arn:aws:iot:*:*:topic/$aws/things/{}/shadow/*'.format(THING_NAME),
              'arn:aws:iot:*:*:topic/dt/{}/heartbeat'.format(THING_NAME)
          ]
      },
      {
          'Effect': 'Allow',
          'Action': [
              'iot:Subscribe'
          ],
          'Resource': [
              'arn:aws:iot:*:*:topicfilter/$aws/things/{}/shadow/*'.format(THING_NAME)
          ]
      },
      {
          'Effect': 'Allow',
          'Action': [
              'iot:Connect'
          ],
          'Resource': [
              'arn:aws:iot:*:*:client/{}'.format(THING_NAME)
          ]
      },
      {
          'Effect': 'Allow',
          'Action': [
              'greengrass:Discover'
          ],
          'Resource': [
              'arn:aws:iot:*:*:thing/{}'.format(THING_NAME)
          ]
      }
  ]
}

iot_client = boto3.client('iot')
gg_client = boto3.client('greengrassv2')

# request AWS IoT Core for new x.509 key pair
cert_and_keys_response = iot_client.create_keys_and_certificate(
  setAsActive=True
)

# write the certificate file to disk
cert = io.open(CERT_FILENAME, 'w')
cert.write(cert_and_keys_response['certificatePem'])
cert.close()

# write the private key file to disk
private_key = io.open(KEY_FILENAME, 'w')
private_key.write(cert_and_keys_response['keyPair']['PrivateKey'])
private_key.close()

# fetch the Amazon Root Certificate Authority 
urllib.request.urlretrieve(ROOTCA_URL, ROOTCA_FILENAME)

# create a new IoT policy for this client device
iot_client.create_policy(
  policyName=IOT_POLICY_NAME,
  policyDocument=json.dumps(IOT_POLICY_DOC)
)

# create a new IoT thing
iot_client.create_thing(
  thingName=THING_NAME
)

# attach the IoT policy to the certificate, granting it permissions
iot_client.attach_policy(
  policyName=IOT_POLICY_NAME,
  target=cert_and_keys_response['certificateArn']
)

# attach the certificate to the IoT thing, binding the device name to the certificate ID
iot_client.attach_thing_principal(
    thingName=THING_NAME,
    principal=cert_and_keys_response['certificateArn']
)

# update the Greengrass Core to recognize this device for local discovery
response = gg_client.batch_associate_client_device_with_core_device(
    entries=[
        {
            'thingName': THING_NAME
        },
    ],
    coreDeviceThingName=CORE_NAME
)
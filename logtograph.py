import paho.mqtt.client as mqtt
import json
from pprint import pprint

import ConfigParser

import zutils
import zmqtt
import sys
import threading
import datetime
import csv
import sys

"""
Knapp
evt/zwave/usb0/node/8/basic/set {"value": 255}
#ingen report

Rorelse
evt/zwave/usb0/node/11/sensor_alarm/report {"type": "general_purpose", "source_node": 11, "value": 255, "seconds": 144}

Light
evt/zwave/usb0/node/11/sensor_multilevel/report {"type": "luminance", "value": 599.0, "scale": "lx"}

Temp
#obj/zwave/usb0/node/11/sensor_multilevel {"timestamp": 1431005441, "scale": "C", "type": "air_temperature", "value": 27.29}
evt/zwave/usb0/node/11/sensor_multilevel/report {"type": "air_temperature", "value": 27.299999237060547, "scale": "C"}

Dorr
evt/zwave/usb0/node/9/basic/set {"value": 255}

Flood
evt/zwave/usb0/node/4/sensor_alarm/report {"type": "general_purpose", "source_node": 4, "value": 255, "seconds": 144}


Power
evt/zwave/usb0/node/2/meter/report {"meter_type": "electric_meter", "rate_type": "import", "scale": "kWh", "value": 0.0}

Switch
evt/zwave/usb0/node/2/switch_binary/report {"switch": true}

Power
evt/zwave/usb0/node/3/sensor_multilevel/report {"type": "power", "value": 131.0, "scale": "W"}

motion hall
evt/zwave/usb0/node/7/sensor_binary/report {"value": 255}

Dimmer
evt/zwave/usb0/node/5/switch_multilevel/report {u'level': 99}

time,nodeid,nodetype,type,value,raw
2015-05-08 14:15:26.819568,9,basic,basic,255,{u'value': 255}
2015-05-08 14:15:32.313416,9,basic,basic,0,{u'value': 0}
2015-05-08 14:15:39.280514,11,sensor_binary,sensor_binary,0,{u'value': 0}
2015-05-08 14:15:39.331219,11,basic,basic,0,{u'value': 0}
2015-05-08 14:16:23.259764,10,basic,basic,255,{u'value': 255}
2015-05-08 14:16:23.265951,10,alarm,7,0,"{u'type': 7, u'level': 255}"
2015-05-08 14:16:26.427504,12,sensor_binary,sensor_binary,255,{u'value': 255}
2015-05-08 14:16:26.482792,12,basic,basic,255,{u'value': 255}
2015-05-08 14:16:28.064208,10,basic,basic,0,{u'value': 0}
2015-05-08 14:16:28.080888,10,alarm,7,0,"{u'type': 7, u'level': 0}"
2015-05-08 14:17:21.952564,10,basic,basic,255,{u'value': 255}
2015-05-08 14:17:21.970117,10,alarm,7,0,"{u'type': 7, u'level': 255}"
2015-05-08 14:17:26.243708,10,basic,basic,0,{u'value': 0}
2015-05-08 14:17:26.262593,10,alarm,7,0,"{u'type': 7, u'level': 0}"
2015-05-08 14:17:31.817493,9,basic,basic,255,{u'value': 255}
2015-05-08 14:17:37.302479,9,basic,basic,0,{u'value': 0}
2015-05-08 14:17:37.987218,11,sensor_multilevel,luminance,385.0,"{u'scale': u'lx', u'type': u'luminance', u'value': 385.0}"
2015-05-08 14:17:45.159708,11,sensor_binary,sensor_binary,255,{u'value': 255}
2015-05-08 14:17:45.211394,11,basic,basic,255,{u'value': 255}
2015-05-08 14:17:49.956917,12,sensor_binary,sensor_binary,0,{u'value': 0}
2015-05-08 14:17:50.008987,12,basic,basic,0,{u'value': 0}
2015-05-08 14:18:49.728226,11,sensor_binary,sensor_binary,0,{u'value': 0}
2015-05-08 14:18:49.754467,11,basic,basic,0,{u'value': 0}
2015-05-08 14:19:33.175318,11,sensor_binary,sensor_binary,255,{u'value': 255}
2015-05-08 14:19:33.226709,11,basic,basic,255,{u'value': 255}


"""

argc = len(sys.argv)
if argc < 2:
	print("missing filename")
	sys.exit(1)

filename = sys.argv[1]

with open(filename, 'rb') as csvfile:
	reader = csv.DictReader(csvfile)
	for dic in reader:
		print (dic)


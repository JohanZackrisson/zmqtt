import paho.mqtt.client as mqtt
import json
from pprint import pprint

import ConfigParser

import zutils
import zmqtt
import sys
import threading
import datetime
import csvlog
import time
import os
import ssl
import visualize_data
import socket
import mongolog
from datainterface import DataInterface

mq = zmqtt.zmqtt()

eventlog = csvlog.ZLogCustom("event.log", [ 'time', 'nodeid', 'nodetype', 'type', 'value', 'raw'])
log = csvlog.ZLog("mqttevents.log")

mongolog = mongolog.MongoLog("logdata", "event_log")

"""
class MongoData(DataInterface):
	def Data(self):
		out = [] 
		for item in mongolog.Query().sort("time", -1).limit(100):
			del item["_id"]
			out.append(item)
		return out
	def LastUpdate(self):
		return mongolog.LastUpdate()

ds = visualize_data.VisualizationServer(socket.gethostname(), 8081, MongoData())
ds.ServeInBackground()
"""

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

"""

config = ConfigParser.ConfigParser()
config.read('config.cfg')

organization = config.get("ibm", "organization")
appId = config.get("ibm", "appid")
servername = config.get("ibm", "servername")
username = config.get("ibm", "username")
password = config.get("ibm", "password")

clientid = "a:{}:{}".format(organization, appId)
print("IBM Clientid: " + clientid)
ibm_mqtt = zmqtt.zmqtt(clientId = clientid)

caFile = os.path.dirname(os.path.abspath(__file__)) + "/messaging.pem"
#self.client.tls_set(ca_certs=caFile, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
ibm_mqtt.mqtt.tls_set(ca_certs=caFile, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
ibm_mqtt.mqtt.username_pw_set(username, password)

ibm_mqtt.connect(servername, 8883)
ibm_mqtt.startBackground()

IBM_FORMAT="iot-2/type/{}/id/{}/evt/status/fmt/json"

def publish_ibm(nodeid, nodetype, evttype, value, rawdata):
	data = {
		'd': {
			'nodeid' : nodeid,
			'nodetype' : nodetype,
			'eventtype' : evttype,
			'value' : value,
			'raw' : rawdata,
			nodetype: { evttype: value }
		},
		'ts': datetime.datetime.now().isoformat()
	}

	topic = IBM_FORMAT.format("sensor", nodeid)
	ibm_mqtt.publish(topic, data)
	print("IBM data: ", topic, data)

def logEvent(nodeid, nodetype, evttype, value, rawdata):
	# [ 'time', 'nodeid', 'nodetype', 'type', 'value', 'raw']
	data = { 'time': eventlog.FmtTimeNow(), 'nodeid' : nodeid, 'nodetype': nodetype, 'type': evttype, 'value': value, 'raw': str(rawdata) }
	eventlog.WriteEvent(data)
	publish_ibm(nodeid, nodetype, evttype, value, rawdata)
	#ds.GetStore().Add(data)
	mongolog.Log(data)
	print(nodeid, nodetype, evttype, value)

@mq.trigger("#", json=False)
def all(topic, data):
	print("debug: %s %s %s" % (eventlog.FmtTimeNow(), topic, data) )
	log.WriteEvent(topic, data)

@mq.trigger("evt/zwave/+/node/+/+/report")
def evtReport(topic, data):
	topicinfo = topic.split('/')
	nodeid = topicinfo[4]
	nodetype = topicinfo[5]

	print("evt report %s %s" % (topic, data))
	type = data["type"] if "type" in data else "unknown"
	value = data["value"] if "value" in data else 0

	if nodetype in ("switch_binary"):
		type = nodetype
		value = int(data["switch"]) if "switch" in data else 0

	if nodetype in ("sensor_binary"):
		type = nodetype
		value = int(data["value"]) if "value" in data else 0

	if nodetype in ("switch_multilevel"):
		type = nodetype
		value = int(data["level"]) if "level" in data else 0

	print("%s %s %s %s %s" % (eventlog.FmtTimeNow(), nodeid, nodetype, type, value))
	
	logEvent(nodeid, nodetype, type, value, data)


@mq.trigger("evt/zwave/+/node/+/basic/set")
def basicSet(topic, data):
	topicinfo = topic.split('/')
	nodeid = topicinfo[4]
	nodetype = "basic"
	type = "basic"
	value = data["value"] if "value" in data else 0

	print("evt report %s %s" % (topic, data))
	print("%s %s %s %s" % (nodeid, nodetype, type, value))

	logEvent(nodeid, nodetype, type, value, data)


"""
@mq.trigger("obj/zwave/+/node/+/switch")
def switch(topic, data):
	topicinfo = topic.split('/')
	nodeid = topicinfo[5]
	if ("value" in data):
		logEvent(nodeid, "switch", data["value"])

"""

#mq.connect("test.mosquitto.org", 1883)
mq.connect("192.168.1.1", 1883)
mq.startBackground()

while(True):
	time.sleep(1)



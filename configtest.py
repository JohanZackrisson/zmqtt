import paho.mqtt.client as mqtt
import json
from pprint import pprint

import ConfigParser

import zutils
import zmqtt
import sys
import threading
import datetime
import time

mq = zmqtt.zmqtt()

@mq.trigger("#", json=False)
#@mq.trigger("+/zwave/usb0/node/5/#", json=False)
def all(topic, data):
	print("debug: %s %s" % (topic, data) )


@mq.trigger("evt/zwave/usb0/node/8/basic/set")
def button(topic, data):
	print "button pressed"
	#topic = "obj/zwave/usb0/node/11/configuration/2"
	topic = "set/obj/zwave/usb0/node/11/configuration/2"
	#topic = "evt/zwave/usb0/node/11/configuration/report"
	data = { "parameter":int(2), "value": 15, "size": 1, "timestamp": int(time.time())}
	#data = { }
	mq.publish(topic, data, "json", 2, 1)

	topic = "get/obj/zwave/usb0/node/11/configuration"
	data = { "parameter":int(2), "timestamp": int(time.time())}
	mq.publish(topic, data, "json", 2, 0)

mq.connect("192.168.1.1", 1883)
mq.start()


"""
def update_pending(daemon, nid, cmd, value):
	topic = "obj/zwave/"+daemon+"/node/"+nid+"/"+cmd
	obj = rules.obj(topic)
	obj.update({"pending": {"timestamp": rules.timestamp() , "value": value}})
	mqtt.publish(topic, obj, 2, 1)
	print topic, obj

@rules.triggers("evt/zwave/+/node/+/configuration/report")
def configuration_report(path, obj):
	obj.update({"timestamp": int(time.time())})
	topic = "obj/zwave/"+path[2]+"/node/"+path[4]+"/configuration/"+str(obj["parameter"])
	rules.export(topic, obj)

@rules.triggers("set/obj/zwave/+/node/+/configuration/+")
def configuration_report(path, obj):
	if obj_set(path[3], path[5], "configuration", "set", {"parameter":int(path[7]), "value": obj["value"], "size": obj["size"]}, False):
		update_pending(path[3], path[5], "configuration/" + path[7], obj["value"])
	obj_set(path[3], path[5], "configuration", "get", {"parameter":int(path[7])}, False)


"""
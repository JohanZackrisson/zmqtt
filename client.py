import paho.mqtt.client as mqtt
import json
from pprint import pprint

import zutils

#class MQTTClient():
	
onoff = False

def on_connect(mqttc, obj, rc):
	mqttc.subscribe("#", 0)
	print("------------------------------------------")
	print("------------------------------------------")
	print("------------------------------------------")
	#mqttc.publish("cmd/zwave/usb0/node/3/switch_binary/set", '{"switch": true}')
	#mqttc.publish("cmd/zwave/usb0/node/3/sensor_multilevel/get", '{}');
	#mqttc.publish("cmd/zwave/usb0/node/3/sensor_multilevel/get", '{}');
	#mqttc.publish("set/obj/house/hemma/2/switch", '{ "value" : 0 }')
	#mqttc.publish("set/obj/zwave/usb0/node/5/dimmer", '{"level": 1}')
	
	print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
	global onoff
	#print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
	print(msg.topic+" "+str(msg.qos))
	try:
		#print(msg.payload)
		jsondata = json.loads(str(msg.payload))
		pprint(jsondata)
	except ValueError:
		print("not json, ValueError")
	except TypeError:
		print("not json, TypeError")
	
	foo = """if msg.topic == "evt/zwave/usb0/node/7/sensor_binary/report":
		#mqttc.publish("cmd/zwave/usb0/node/5/switch_binary/set", '{"switch": ' + ('false', 'true')[onoff] + '}')
		mqttc.publish("set/obj/zwave/usb0/node/5/dimmer", '{"level": '+ ('20', '70')[onoff] + '}')
		onoff = not onoff"""

	foo = """if msg.topic == "evt/zwave/usb0/node/9/basic/set":
		opened = jsondata["value"] == 255
		mqttc.publish("set/obj/house/hemma/3/switch", '{ "value" : ' + ('false', 'true')[opened] + ' }')
	"""

def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print("Log: " + string)

'''
# If you want to use a specific client id, use
# mqttc = mosquitto.Mosquitto("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
#mqttc.on_log = on_log
mqttc.connect("test.mosquitto.org", 1883, 60)

#mqttc.subscribe("string", 0)
#mqttc.subscribe(("tuple", 1))
#mqttc.subscribe([("list0", 0), ("list1", 1)])

mqttc.loop_forever()
'''

def startClient():
	print("starting client")
	cl = mqtt.Client()
	cl.on_message = on_message
	cl.on_connect = on_connect
	cl.on_publish = on_publish
	cl.on_subscribe = on_subscribe
	
	cl.connect("test.mosquitto.org", 1883, 60)
	#cl.connect("194.47.149.203", 1883, 60)
	#cl.connect("192.168.1.1", 1883, 60)
	cl.loop_forever()

def test():
	mq.addDatabaseCollector(db)
	mq.addAction("/foo/bar/#/battery", warnOnLowBattry())
	mq.addAction("/baz/fuz/#/motion_sensor", light.turnLightsOnFor(mqttc, "node8", 60))


if __name__=='__main__':
	startClient()

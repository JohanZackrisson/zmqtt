import paho.mqtt.client as mqtt
import json
from pprint import pprint

import ConfigParser

import zutils
import zmqtt
import sys
import threading
import datetime

########################################

class Sensor(object):
	def __init__(self, mq, prefix, nodeid, type):
		if not prefix or not nodeid:
			raise Exception("invalid parameters")
		self.mq = mq
		self.prefix = prefix
		self.nodeid = nodeid
		self.type = type
		self._data = {}
	
	def getObjTopic(self):
		return "obj/%s/node/%i/%s" % (self.prefix , self.nodeid, self.type )
	def getEvtTopic(self):
		return "evt/%s/node/%i/%s/report" % (self.prefix , self.nodeid, self.type )

	def trigger(self):
		def trigdec(func):
			@self.mq.trigger(self.getObjTopic())
			def wrapper(topic, data):
				self._data = data
				func(data)
			return wrapper
		return trigdec

	def value(self):
		if "value" in self._data:
			return self._data["value"]
		return None

class Actuator(object):
	def __init__(self, mq, prefix, nodeid, type):
		if not prefix or not nodeid:
			raise Exception("invalid parameters")
		self.mq = mq
		self.prefix = prefix
		self.nodeid = nodeid
		self.type = type

	def getCmdTopic(self):
		return "cmd/%s/node/%i/%s/set" % (self.prefix , self.nodeid, self.type )

	def publish(data):
		self.mq.publish(self.getCmdTopic(), data)

########################################

class SwitchBinary(object):
	def __init__(self, mq, prefix, nodeid):
		if not prefix or not nodeid:
			raise Exception("invalid parameters")
		self.mq = mq
		self.prefix = prefix
		self.nodeid = nodeid
		self._isOn = False
		
		# subscribe to update events
		@self.mq.trigger(self.getObjTopic())
		def switchtrigger(topic, data):
			print(str(data))
			if data and "switch" in data and int(data["switch"]) > 0:
				self._isOn = True
			else:
				self._isOn = False
			print("switchbinary event triggered: %s" % self._isOn)


	# note that this is listening to the switch and not switch_binary
	def getObjTopic(self):
		return "obj/%s/node/%i/switch" % (self.prefix, self.nodeid)

	def getCmdTopic(self):
		return "cmd/%s/node/%i/switch_binary/set" % (self.prefix , self.nodeid )

	def getEvtTopic(self):
		return "evt/%s/node/%i/switch_binary/report" % (self.prefix , self.nodeid )

	def set(self, on):
		data = { "switch": on }
		self.mq.publish(self.getCmdTopic(), data)
	
	def isOn(self):
		return self._isOn

	# return a trigger function for this switch
	def trigger(self, q):
		def triggerfunc(func):
			pass
		return triggerfunc
		pass

	def trigger(self):
		def trigdec(func):
			@self.mq.trigger(self.getEvtTopic())
			def wrapper(topic, data):
				func(data)
			return wrapper
		return trigdec

#evt/zwave/usb0/node/7/sensor_binary/report
class SensorBinary(object):
	def __init__(self, mq, prefix, nodeid):
		self.mq = mq
		self.prefix = prefix
		self.nodeid = nodeid
		#self.value = -1
		self._data = {}
	
	"""
		@self.mq.trigger(self.getObjTopic())
		def sensortrigger(topic, data):
			if data and "value" in data:
				self.value = int(data["value"])
			else:
				self.value = -1
			print("sensor_binary value changed: ", self.value)
	

	def getValue(self):
		return self.value
	"""

	def getEvtTopic(self):
		return "evt/%s/node/%i/sensor_binary/report" % (self.prefix, self.nodeid)

	def getObjTopic(self):
		return "obj/%s/node/%i/sensor_binary" % (self.prefix, self.nodeid)

	def trigger(self):
		def trigdec(func):
			@self.mq.trigger(self.getEvtTopic())
			def wrapper(topic, data):
				self._data = data
				func(data)
			return wrapper
		return trigdec

	def value(self):
		if "value" in self._data:
			return self._data["value"]
		return None

class SensorMultilevel(object):
	def __init__(self, mq, prefix, nodeid, type):
		if not prefix or not nodeid:
			raise Exception("invalid parameters")
		self.mq = mq
		self.prefix = prefix
		self.nodeid = nodeid
		self._data = {}
		self.type = type
		
		# subscribe to update events
		#@self.mq.trigger(self.getObjTopic())
		def mltrigger(topic, data):
			print(str(data))
			self._data = data
			print("sensor_multilevel event: %s" % self._data)


	# note that this is listening to the switch and not switch_binary
	def getObjTopic(self):
		return "obj/%s/node/%i/%s" % (self.prefix, self.nodeid, self.type)

	def getCmdTopic(self):
		return "cmd/%s/node/%i/%s/set" % (self.prefix , self.nodeid, self.type)

	def getEvtTopic(self):
		return "evt/%s/node/%i/%s/report" % (self.prefix , self.nodeid, self.type)

	def set(self, data):
		self.mq.publish(self.getCmdTopic(), data)

	def get(valuename):
		if valuename in self._data:
			return self._data[valuename]
		return None

	def value(self):
		if "value" in self._data:
			return self._data["value"]
		return None
	
	# return a trigger function for this switch
	"""
	def trigger(self, q):
		def triggerfunc(func):
			pass
		return triggerfunc
		pass
	"""
	def trigger(self):
		def trigdec(func):
			@self.mq.trigger(self.getEvtTopic())
			def wrapper(topic, data):
				self._data = data
				func(data)
			return wrapper
		return trigdec

class LightSensor(SensorMultilevel):
	def __init__(self, mq, prefix, nodeid):
		super(LightSensor, self).__init__(mq, prefix, nodeid, "sensor_multilevel")

	def trigger(self):
		def trigdec(func):
			@self.mq.trigger(self.getEvtTopic())
			def wrapper(topic, data):
				# FIXME: This might not be right, check!!!!
				if "luminance" in data:
					self._data = data
				func(data)
			return wrapper
		return trigdec

class TempSensor(SensorMultilevel):
	def __init__(self, mq, prefix, nodeid):
		super(LightSensor, self).__init__(mq, prefix, nodeid, "sensor_multilevel")

	def trigger(self):
		def trigdec(func):
			@self.mq.trigger(self.getEvtTopic())
			def wrapper(topic, data):
				if "air_temperature" in data:
					self._data = data
				func(data)
			return wrapper
		return trigdec


#motion sensor is just an alias for a SensorBinary for now
class MotionSensor(SensorBinary):
	pass

class Button(Sensor):
	def __init__(self, mq, prefix, nodeid):
		super(Button, self).__init__(mq, prefix, nodeid, "basic")

class Dimmer(SensorMultilevel):
	def __init__(self, mq, prefix, nodeid):
		super(Dimmer, self).__init__(mq, prefix, nodeid, "switch_multilevel")

	def setLevel(self, level):
		data = {"shortdim": 0, "level": level}
		self.set(data)

mq = zmqtt.zmqtt()

config = ConfigParser.ConfigParser()
config.read("equipment.cfg")

#def EqConfig(config, name):
#	return { "prefix": config.get("Global", "prefix"), "nodeid": config.get(name, "nodeid") }

prefix = config.get("Global", "prefix")

s1 = SwitchBinary(mq, prefix, config.getint("Plugg 1", "nodeid"))
#s1.set(mq, on=True)

#s2 = SwitchBinary(mq, prefix, config.getint("Dimmer 1", "nodeid"))
#s2.set(on=True)

ms1 = SensorBinary(mq, prefix, config.getint("Motion Sensor 1", "nodeid"))

#@ms1.trigger()
def motionTrigger(data):
	#pprint(data)
	if ms1.getValue() > 0:
	#if data and data["value"] == 255:
		print("Motion sensor triggered")
		#s1.set(on=True)
		to = not s1.isOn()
		s1.set(on=to)

#@s1.trigger()
def somebodySwitched(data):
	print("switched:" , s1.isOn())


@mq.trigger("#", json=False)
#@mq.trigger("+/zwave/usb0/node/5/#", json=False)
def all(topic, data):
	print("debug: %s %s" % (topic, data) )

#@mq.trigger("+/zwave/usb0/node/11/#")
#@mq.trigger("+/zwave/usb0/node/5/#", json=False)
def logMotion(topic, data):
	print("-----------------------")
	print("MOTION SENSOR debug: %s %s" % (topic, data) )
	print("-----------------------")

##############################################################################################

class HouseState(object):
	def __init__(self):
		self._location = "Unknown"
		self._timeOfFall = None
		self._timer = False
		self._lowlight = False
	
	def TrackLocation(self, loc):
		print("-------------------------")
		print("Location changed to %s" % (loc))
		print("-------------------------")
		self._location = loc
		# When moving, the person must be in field of vision of one of the motion sensors
		# thus it can't be a urgent incident
		if self._timer:
			self._timer.cancel()
			self._timer = False

		if self._lowlight:
			# FIXME: add timer to turn off light after X minutes
			dimmer_livingroom.setLevel(99)

	def FallDetected(self):
		self._timeOfFall = datetime.datetime.now()
		print("-------------------------")
		print("Someone has fallen in %s %s" % (self._location, self._timeOfFall))
		print("-------------------------")

		dimmer_livingroom.setLevel(99)

		if self._timer:
			self._timer.cancel()
		#timer = threading.Timer(5*60.0, UrgentHelpNeeded)
		self._timer = threading.Timer(5.0, self.UrgentHelpNeeded)
		self._timer.start();

	def UrgentHelpNeeded(self):
		print("-------------------------")
		print("URGENT: Send help to XXYY, person has fallen and has not moved for 5 min. Location %s" % (self._location))
		print("-------------------------")

	def SetLightLevel(self, level):
		print("light changed %s" % (level))
		self._lowlight = level < 50
		print("low light? %s" % self._lowlight)

state = HouseState()

motion_kitchen = MotionSensor(mq, prefix, config.getint("Motion Sensor 1", "nodeid"))
motion_bathroom = MotionSensor(mq, prefix, config.getint("Motion Sensor 3", "nodeid"))
motion_livingroom = MotionSensor(mq, prefix, config.getint("Motion Sensor 2", "nodeid"))
alarmbutton = Button(mq, prefix, config.getint("Alarm Button 1", "nodeid"))
light_livingroom = LightSensor(mq, prefix, config.getint("Motion Sensor 2", "nodeid"))

dimmer_livingroom = Dimmer(mq, prefix, config.getint("Dimmer 1", "nodeid"))

@motion_kitchen.trigger()
def motion_in_kitchen(data):
	if motion_kitchen.value() > 0:
		state.TrackLocation("Kitchen")

@motion_bathroom.trigger()
def motion_in_bathroom(data):
	if motion_bathroom.value() > 0:
		state.TrackLocation("Bathroom")

@motion_livingroom.trigger()
def motion_in_livingroom(data):
	if motion_livingroom.value() > 0:
		state.TrackLocation("Livingroom")

@alarmbutton.trigger()
def alarm_triggered(data):
	if alarmbutton.value() > 0:
		state.FallDetected()
	else:
		# if downpress, just turn off the lights
		#setDimmer(dimmer, 0)
		dimmer_livingroom.setLevel(0)

@light_livingroom.trigger()
def light_changed(data):
	ll = light_livingroom.value()
	state.SetLightLevel(ll)

#mq.connect("test.mosquitto.org", 1883)
mq.connect("192.168.1.1", 1883)
mq.start()



#setDimmer(dimmer, 0)

'''
security_alarm = SomeSensor(mq, prefix, config.getint("Trygghetslarm 1", "nodeid"))
severity = 0
alarmCount = 0
alarmWhen = 0
lastSeenIn = "unknown"

@security_alarm.trigger()
def has_fallen_trigger(data):
	print("Agda has fallen, please help her")
	severity = 1
	alarmCount += 1
	alarmWhen = datetime.datetime.now()

	# turn on lights
	s1.set(on = True)

	# start camera?

	# start checking for movement
	checkForMovement = True

@motion.trigger()
def has_moved(data):
	if not checkForMovement:
		return


'''

#what is needed to get things running?
# - activation of trigger when fall or alarm is sent from the safety alarm
# - 



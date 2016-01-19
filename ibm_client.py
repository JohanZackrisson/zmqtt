import ibmiotf.device
import time

organization = "doe5jg"
deviceType = "atypedefinedonline"
deviceId = "somefakedeviceid"
authMethod = "token"
authToken = "1234567"

"""
def myCommandCallback(cmd):
  print("Command received: %s" % cmd.data)
  if cmd.command == "setInterval":
    if 'interval' not in cmd.data:
      print("Error - command is missing required information: 'interval'")
    else:
      interval = cmd.data['interval']
  elif cmd.command == "print":
    if 'message' not in cmd.data:
      print("Error - command is missing required information: 'message'")
    else:
      print(cmd.data['message'])
"""


deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
deviceCli = ibmiotf.device.Client(deviceOptions)

#deviceCli.commandCallback = myCommandCallback

deviceCli.connect()
print("connected!")

#deviceCli.setErrorCode(1).wait()
#deviceCli.clearErrorCodes()

myData = { 'hello' : 'world', 'x' : 23}

while True:
	time.sleep(1)
	deviceCli.publishEvent(event="status", msgFormat="json", data=myData)
	print(".")
import visualize_data
import mongolog
import time
import socket
from datainterface import DataInterface

mongolog = mongolog.MongoLog("logdata", "event_log")

class MongoData(DataInterface):
	def Data(self):
		out = [] 
		for item in mongolog.Query().sort("time", -1).limit(100):
			del item["_id"]
			out.append(item)
		return out
	def LastUpdate(self):
		return mongolog.LastUpdate()

ds = visualize_data.VisualizationServer("0.0.0.0", 8081, MongoData())
ds.ServeInBackground()

while True:
	time.sleep(1)
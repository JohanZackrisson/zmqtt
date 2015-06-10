import csv
import os.path
from time import strftime
import datetime

#from pprint import pprint

class ZLogCustom(object):
	def __init__(self, filename, fields):
		self._filename = filename
		self._file = self._createFile(self._filename)

		self._writer = csv.DictWriter(self._file, fieldnames=fields)
		self._writer.writeheader()

	def __del__(self):
		self._file.close()

	def _createFile(self, name):
		if os.path.isfile(name):
			suffix = strftime("%Y%m%d-%H%M%S")
			os.rename(name, name + "_" + suffix)
		return open(name, 'w')

	@staticmethod
	def FmtTimeNow():
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

	def WriteEvent(self, row):
		#time = strftime("%Y-%m-%d %H:%M:%S")
		#dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
		#.isoformat()
		#print(dtime)
		self._writer.writerow(row)


class ZLog(object):
	def __init__(self, filename):
		fields = [ 'time', 'topic', 'data']
		self._filename = filename
		self._file = self._createFile(self._filename)

		self._writer = csv.DictWriter(self._file, fieldnames=fields)
		self._writer.writeheader()

	def __del__(self):
		self._file.close()

	def _createFile(self, name):
		if os.path.isfile(name):
			suffix = strftime("%Y%m%d-%H%M%S")
			os.rename(name, name + "_" + suffix)
		return open(name, 'w')

	def WriteEvent(self, topic, data):
		#time = strftime("%Y-%m-%d %H:%M:%S")
		dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
		#.isoformat()
		#print(dtime)
		self._writer.writerow({'time': dtime, 'topic': topic, 'data': data})

class ZReadLog(object):
	def __init__(self, filename):
		self._filename = filename

	def ReadEvents(self):
		fields = [ 'time', 'topic', 'data']
		out = []

		with open(self._filename) as csvfile:
			reader = csv.DictReader(csvfile)
			#print(reader)
			for row in reader:
				#print(row)
				out.append(row)
		return out

class ZEventFilter(object):
	def __init__(self, data):
		self._data = data[:]

	def __iter__(self):
		return self

	def _transform(self, elem):
		return elem

	def next(self):
		if len(self._data) == 0:
			raise StopIteration

		elem = self._data[0]
		self._data.pop(0)

		return self._transform(elem)

def test():
	log = ZLog("log.csv")
	log.WriteEvent("testtopic", "testdata")
	log.WriteEvent("testtopic  2", "testdata2")
	log.WriteEvent("testtopic %s1234(()#)''',,,,,222??3", "testdata3")
	del log # closes the file..

	inlog = ZReadLog("log.csv")
	#print(inlog.ReadEvents())
	for x in ZEventFilter(inlog.ReadEvents()):
		print(x)

if __name__=='__main__':
	test()
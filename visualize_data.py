import time
import BaseHTTPServer
import socket
import threading
import json
from os import curdir, sep
import urlparse
from SocketServer import ThreadingMixIn

class DataStorage(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._store = []
        self._lastUpdate = 0
    def Add(self, data):
        self._lock.acquire()
        try:
            self._lastUpdate = time.time()
            self._store.append( (self._lastUpdate,data) )
        finally:
            self._lock.release()
    def GetSince(self, since):
        out = []
        self._lock.acquire()
        try:
            out = [val for key, val in self._store if key > since]
        finally:
            self._lock.release()

        return out
    def LastUpdated(self):
        return self._lastUpdate
    def Prune():
        pass

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    _data = None
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        """Respond to a GET request."""

        files = { "/index.html": "index.html",
            "/" : "index.html",
            "/timeline-min.js": "timeline-min.js",
            "/timeline.js": "timeline.js",
            "/timeline.css": "timeline.css"
            }
        if self.path in files:
            self._ServeFile(files[self.path])
            return

        if self.path.startswith("/api/data"):
            self._ServeData()
            return

        self.send_error(404,'File Not Found: %s' % self.path)

    def _ServeFile(self, filename):
        f = open(curdir + sep + "static" + sep + filename)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

    def _ServeData(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        url = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(url.query)
        since = int(query["since"][0]) if "since" in query else 0
        data = { 'data': self._data.GetSince(since), 'lastUpdate': int(self._data.LastUpdated()) }
        self.wfile.write(json.dumps(data))

class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""

class DataStoreServer(object):
    def __init__(self, listenOn, port):
        self._datastore = DataStorage()
        self._listenOn = listenOn
        self._port = port
        pass

    def ServeInBackground(self):
        MyHandler._data = self._datastore
        self._server = ThreadedHTTPServer((self._listenOn,self._port), MyHandler)

        server_thread = threading.Thread(target=self._server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def GetStore(self):
        return self._datastore

    def Close(self):
        self._server.shutdown()
        self._server.server_close()

if __name__ == '__main__':
    HOST_NAME = socket.gethostname() # 'example.net' # !!!REMEMBER TO CHANGE THIS!!!
    PORT_NUMBER = 8081 # Maybe set this to 9000.

    ds = DataStoreServer(HOST_NAME, PORT_NUMBER)
    ds.GetStore().Add({'some': 'data', 'something': 'else'})
    ds.ServeInBackground()

    while True:
        time.sleep(1)
        print(".")
        ds.GetStore().Add({'some': 'data', 'something': 'else'})


    """datastore = DataStorage()
    datastore.Add({'some': 'data', 'something': 'else'})

    server_class = BaseHTTPServer.HTTPServer
    MyHandler._data = datastore
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
    """
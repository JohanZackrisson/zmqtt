# import json
import cherrypy
# from cherrypy._cpcompat import json
from cherrypy import tools
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket, WebSocket
import os
import mongolog
import datetime
from ws4py.messaging import TextMessage
import json

cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


eventlog = mongolog.MongoLog("logdata", "event_log")
highspeedlog = mongolog.MongoLog("logdata", "high_log")


class WebAPI(object):

    @cherrypy.expose
    def index(self):
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data(self):
        out = []
        for item in eventlog.Query().sort("time", -1).limit(100):
            del item["_id"]
            out.append(item)
        data = {'data': out, 'lastUpdate': int(eventlog.LastUpdate())}
        return data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def motion(self):
        start = 0
        end = 9000000000000
        if cherrypy.request.method == "POST":
            json_input = cherrypy.request.json
            if not "start" in json_input or not "end" in json_input:
                raise cherrypy.HTTPError(400, "Missing parameters")
            start = int(json_input["start"])
            end = int(json_input["end"])

        out = []
        for item in highspeedlog.Collection().find({"time": {"$gt": start, "$lt": end}}).sort("time", 1).limit(1000):
            del item["_id"]
            out.append(item)
        return out


class WebAPIReport(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def location(self):
        if cherrypy.request.method == "POST":
            # print(cherrypy.request.json)
            json_input = cherrypy.request.json
            if not "id" in json_input or not "location" in json_input:
                raise cherrypy.HTTPError(400, "Missing parameters")
            self._ReportLocation(json_input["id"], json_input["location"])
            return {"result": "Reported"}

        return {"result": "OK"}

    def _ReportLocation(self, id, location):
        data = {
            'time': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+01:00"),
            'nodeid': id,
            'nodetype': 'browser',
            'type': 'location',
            'value': location,
            'raw': {'id': id, 'location': location}
        }
        eventlog.Log(data)


class Root(object):

    @cherrypy.expose
    def index(self):
        return 'some HTML with a websocket javascript connection'

    @cherrypy.expose
    def ws(self):
        # whatever you do, don't return any text here!
        # handler = cherrypy.request.ws_handler
        pass


class MyWebSocket(WebSocket):
    # count = 0

    def __init__(self, *args, **kwargs):
        super(MyWebSocket, self).__init__(*args, **kwargs)
        self._lastSend = None

    def received_message(self, message):
        if isinstance(message, TextMessage):
            s = str(message)
            try:
                obj = json.loads(s)
            except ValueError:
                return

            type = obj["type"]
            if type == "motion":
                # print(self.count)
                # self.count = self.count + 1
                highspeedlog.Log(obj)

        # self.send(message.data, message.is_binary)
        # self.send("Hello", False)
        if not self._lastSend:
            self._lastSend = datetime.datetime.now()

        if datetime.datetime.now() > self._lastSend + datetime.timedelta(milliseconds=200):
            print("broadcast")
            cherrypy.engine.publish('websocket-broadcast', message)
            self._lastSend = datetime.datetime.now()

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))


cwd_dir = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

cherrypy.config.update({
    'tools.staticfile.root': cwd_dir,
    'tools.staticdir.root': cwd_dir
})


cherrypy.tree.mount(WebAPI(), '/api')
cherrypy.tree.mount(WebAPIReport(), '/api/report')

cherrypy.quickstart(Root(), '/', config={
    '/ws': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': MyWebSocket,
        'tools.websocket.protocols': ['acceleration', 'gyroscope']
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static'
    },
    '/index.html': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': "static/index.html"
    }
})

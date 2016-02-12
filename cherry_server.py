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

cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


mongolog = mongolog.MongoLog("logdata", "event_log")


class WebAPI(object):

    @cherrypy.expose
    def index(self):
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data(self):
        out = []
        for item in mongolog.Query().sort("time", -1).limit(100):
            del item["_id"]
            out.append(item)
        data = {'data': out, 'lastUpdate': int(mongolog.LastUpdate())}
        return data


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
        mongolog.Log(data)


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

    def received_message(self, message):
        #self.send(message.data, message.is_binary)
        #self.send("Hello", False)
        cherrypy.engine.publish('websocket-broadcast', message)

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

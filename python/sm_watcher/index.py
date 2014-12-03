import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options

import os.path
import json

from tornado.options import define, options
from tornado.ioloop import PeriodicCallback
define("port", default=9000, help="run on the given port", type=int)

from sm_watcher import db

class Entries(object):
   callbacks = []

   def register(self, callback):
       self.callbacks.append(callback)

   def unregister(self, callback):
       self.callbacks.remove(callback)

   def notifyCallbacks(self):
       for callback in self.callbacks:
           callback(self.getEntries())

   def getEntries(self):
       entries = [db.hgetall(name) for name in db.keys()]
       entries.sort(key=lambda x: x['url'], reverse=True)
       return entries


class Application(tornado.web.Application):
    def __init__(self):
        self.entries = Entries()
        handlers = [
            (r"/", IndexHandler),
            (r"/ws", WSHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={'show_entry': ShowEntryModule},
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", ws_url='ws://o4bs.com:9000/ws')

class ShowEntryModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('modules/entries.html')

    def javascript_files(self):
        return "scripts/entries.js"

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'open connection'
        self.send_entries()
        self.callback = PeriodicCallback(self.send_entries, 5000)
        self.callback.start()
        #self.application.entries.register(self.callback)

    def on_close(self):
        print 'close connection'
        #self.application.entries.unregister(self.callback)
        self.callback.stop()

    def on_message(self, message):
        print 'message received %s' % message

    def send_entries(self):
        entries = [db.hgetall(name) for name in db.keys()]
        entries.sort(key=lambda x: x['url'], reverse=True)
        self.write_message(json.dumps(entries))

class EntryModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string('modules/entries.html.html', entry=entry)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

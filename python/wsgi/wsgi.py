import logging
import routes.middleware
import webob.dec
import webob.exc


class Router(object): # base class for WSGI APP, mapping from url to resource

    def __init__(self, mapper=None):
        self.map =  mapper #resource map
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                         self.map) #register url callback
    @classmethod
    def factory(cls, global_conf, **local_conf): # entrance
        return cls() # construct an app

    @webob.dec.wsgify # wrap the request and response in WSGI style
    def __call__(self,req): # callable
        return self._router

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
        # TODO
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app

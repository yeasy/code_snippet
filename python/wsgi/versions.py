import httplib
import json
import webob.dec

from webob import Response

class Controller(object):
    def __init__(self):
        # TODO
        self.version = "0.1"

    def index(self,req):
        response = Response(request=req,
                                  status=httplib.MULTIPLE_CHOICES,
                                  content_type='application/json')
        response.body = json.dumps(dict(versions=self.version))
        return response
            
    @webob.dec.wsgify
    def __call__(self, request):
        # TODO
        return self.index(request)

def create_resource():
    return Controller()

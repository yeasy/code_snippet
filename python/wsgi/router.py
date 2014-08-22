import routes

import wsgi
import versions

class API(wsgi.Router):

    def __init__(self, mapper=None):
        if(mapper == None): # create mapper
            mapper = routes.Mapper()
        versions_resource = versions.create_resource() # create resource
        mapper.connect("/",controller=versions_resource,action="index")# create mapping
        super(API,self).__init__(mapper) 

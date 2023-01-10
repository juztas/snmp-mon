import cherrypy



class HTTPExpose():
    def startwork(self):
        """Start Cherrypy Worker"""
        cherrypy.quickstart(CherryPyThread())


class CherryPyThread():
    @cherrypy.expose
    def index(self):
        """Index Page"""
        return "Hello world!"


if __name__ == '__main__':
    print("WARNING: Use this only for development!")
    cherrypy.quickstart(CherryPyThread())

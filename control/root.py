import cherrypy


class Root(object):
    """
    Expose the / (root) API
    """

    @cherrypy.expose
    def index(self):
        return open('pages/index.html')

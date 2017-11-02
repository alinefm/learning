import cherrypy
import json
import os

from optparse import OptionParser

from control.crawler import Crawler
from control.root import Root


class Server(object):
    """
    Start a cherrypy web server instance 
    """
    def __init__(self, options):
        # Add / and /crawler APIs
        self. webapp = Root()
        self.webapp.crawler = Crawler()

        # Additional APIs configuration
        basepath = os.path.dirname(os.path.realpath(__file__))
        self.config = {
            '/':
                {'tools.trailing_slash.on': False,
                 'error_page.default': self.error_handler},
            '/js':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': os.path.join(basepath, "js")},
            '/css':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': os.path.join(basepath, "css")}
        }

        # Configure cherrypy server according to values entered
        cherrypy.server.socket_host = options.host
        cherrypy.server.socket_port = options.port
        cherrypy.config.update({'global': {'engine.autoreload.on': False}})

    def error_handler(self, status, message, traceback, version):
        # Error handler to return JSON when required
        if 'application/json' in cherrypy.request.headers.get('Accept', []):
            response = cherrypy.response
            response.headers['Content-Type'] = 'application/json'
            return json.dumps({'status': status, 'message': message})

        return cherrypy._cperror.get_error_page()

    def start(self):
        # Start web server
        cherrypy.quickstart(self.webapp, '/', self.config)


if __name__ == '__main__':
    """
    Initialize the web server using cherrypy
    """
    parser = OptionParser()
    parser.add_option('--host', default='127.0.0.1', help='Host IP (default 127.0.0.1)')
    parser.add_option('--port', type="int", default=8080, help='Web server port (default 8080)')
    (options, args) = parser.parse_args()

    srv = Server(options)
    srv.start()

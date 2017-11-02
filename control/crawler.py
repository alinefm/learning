import cherrypy
import json

from model.model import CrawlerModel


class Crawler(object):
    """
    Expose the /crawler API
    """

    def __init__(self):
        # Initialize the model instance
        self.model = CrawlerModel()

    def _cp_dispatch(self, vpath):
        """
        Check if the URI is related to the resource (/crawler/<id>) and
        redirect to it
        """
        if len(vpath) == 1:
            id = vpath.pop(0)
            return Entry(id, self.model)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self, *args, **kwargs):
        """
        Default handler for /crawler API
        """
        method = cherrypy.request.method.upper()
        if method == 'GET':
            return self.get(kwargs)

        raise cherrypy.HTTPError(405, 'Method Not Allowed')

    def get(self, filters):
        """
        Return a list of crawler

        [{"_id": <id>, "url": <url>}, ...]
        """
        data = self.model.getList()
        return json.dumps(data, indent=2, separators=(',', ':'))


class Entry(object):
    """
    Expose the /crawler/<id> API
    """

    def __init__(self, id, model):
        self.id = id
        self.model = model

    @cherrypy.expose
    def index(self, *args, **kwargs):
        """
        Default handler for /crawler/<id> API
        """
        method = cherrypy.request.method.upper()
        if method == 'GET':
            return self.get(kwargs)

        raise cherrypy.HTTPError(405, 'Method Not Allowed')

    def get(self, filters):
        """
        Return Crawlwer details:

        {"_id": <id>, "url": <url>, "refs": [<list of references>]}
        """
        data = self.model.getById(self.id)

        # Allow paginating 'refs' content as it may be too big to send in a
        # single request
        # Use query parameters 'start' and 'limit', for example:
        #   GET /crawler/<id>?start=0&limit=100
        start = int(filters.get('start', 0))
        limit = filters.get('limit')
        limit = limit if limit is None else int(limit) + start

        if limit and limit > len(data['refs']):
            limit = None

        if start > len(data['refs']):
            data['refs'] = []
        else:
            data['refs'] = data['refs'][start:limit]
        return json.dumps(data, indent=2, separators=(',', ':'))

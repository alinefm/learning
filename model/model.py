import cherrypy

from bson.objectid import ObjectId

from database import Database


class CrawlerModel(object):
    """
    Backend implementation for /crawler API
    """

    def __init__(self):
        self.db = Database.getConn()

    def getById(self, id):
        try:
            data = self.db.find_one({'_id': ObjectId(id)})
        except:
            raise cherrypy.HTTPError(404, 'ID not found in crawler')

        if not data:
            raise cherrypy.HTTPError(404, 'ID not found in crawler')
        
        data['_id'] = str(data['_id'])
    
        return data

    def getList(self):
        try:
            data = [{'_id': str(i['_id']), 'url': i['url']}
                    for i in self.db.find(projection={'_id': 1, 'url': 1})] or []
        except:
            raise cherrypy.HTTPError(500, 'Unable to access database to get crawler information')

        return data

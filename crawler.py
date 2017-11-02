import os
import re
import requests
import time

from optparse import OptionParser
from queue import Queue
from threading import Thread
from urllib.parse import urlparse

from database import Database


class Crawler(object):
    """
    Start crawling from a given URL
    """
    def __init__(self, url):
        self.url = url

        # Add or update the database entry for the given URL
        self.db = Database.getConn()
        entry = self.db.find_one({'url': url})
        if entry is None:
            self.db.insert_one({'url': url, 'refs': []})
        else:
            self.db.update({'url': url}, {'refs': []})

        # Queue is being created without a max size to make the processing faster
        # But it may cause memory issues depending on how much data needs to be
        # processed
        self.queue = Queue()
        self.queue.put(url)
        self.visited = []

    def start(self):
        def _finder(obj):
            while not obj.queue.empty():
                # Get url from queue to process it
                url = obj.queue.get()
                if url in obj.visited:
                    obj.queue.task_done()
                    continue

                # Mark url as visited to avoid loops
                obj.visited.append(url)
                try:
                    content = requests.get(url).text
                except Exception:
                    obj.queue.task_done()
                    continue

                # Find all links in the page
                refs = re.findall(r'(?<=<a href=")[^"]*', content)
                for r in refs:
                    # Validate each url
                    pr = urlparse(r)
                    if not pr.path:
                        continue

                    p = urlparse(url)
                    # Build full url according to the parent url
                    # It is to cover the cases when there are internal
                    # references in the page
                    #
                    # In both case, query parameters are being ignored it will
                    # redirect to the same page itself
                    if not pr.scheme or not pr.netloc:
                        res = p.scheme + '://' + p.netloc
                        res += os.path.realpath(p.path + pr.path)
                    else:
                        res = pr.scheme + '://' + pr.netloc + pr.path
                    obj.queue.put(res)
                    self.db.update({'url': obj.url},
                                   {'$addToSet': {'refs': res}})

                print('Crawling from %s: (queue size: %s)' %
                      (obj.url, obj.queue.qsize()))
                obj.queue.task_done()

        # Start 20 threads to make the processing faster
        threads = []
        for i in range(10):
            t = Thread(target=_finder, args=(self,))
            t.setDaemon(True)
            t.start()
            threads.append(t)

            # Wait some time to be able to get more inputs added to queue
            time.sleep(1)

        for t in threads:
            t.join()

        self.queue.join()


if __name__ == '__main__':
    """
    Initialize the crawler service
    """
    parser = OptionParser()
    parser.add_option('--url', default='http://www.google.com',
                      help='URL to start crawling from (default "http://www.google.com")')
    (options, args) = parser.parse_args()

    print('Initializing crawler from %s...' % options.url)
    c = Crawler(options.url)
    c.start()

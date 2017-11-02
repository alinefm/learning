Mini Crawler
=============
It consists into 2 services: one to do the crawl job starting from a given URL
and another one to expose the results in a web application.

The crawler service is defined in ./crawler.py and the web application is defined
in ./server.py.

This solution relies on MongoDB to store the URLs found. You can create a docker
instance for this or running MongoDB in your host system.

The connection to the MongoDB is always done on `localhost:27017` (default configuration)
so if you are working with containers, make sure all them can communicate properly.

I used the `--network=host` option during my tests. I found out it is not a good 
practice due security matters so you may want to create a separated bridge and
get all containers working together.

The web application exposes the following REST APIs:
```
 GET /crawler
    [{"_id": <id>, "url": <entry point url>},
     {"_id": <id>, "url": <entry point url>},
     ...]

 GET /crawler/<id>?start=X&limit=Y
 GET /crawler/<id>
    {"_id": <id>, "url": <entry point url>, "refs": [ <list of references found> ]}

```

Use the `start` and `limit` parameters to enable pagination while getting the
references.

Setup Environment
=================

Use the docker files under /docker directory to build the docker images.

For example:
```
    sudo docker build -f docker/Dockerfile-mongodb -t mongodb .
    sudo docker build -f docker/Dockerfile-crawler -t crawler .
    sudo docker build -f docker/Dockerfile-webapp -t webapp .
```

Then, run each one of the images:
```
    sudo docker run -p 27017:27017 mongodb
    sudo docker run --network=host crawler
    sudo docker run --network=host webapp
```

The crawler entry point is the `crawler.py` script. It accepts an option `--url`
which is the URL to start crawling from. By default, it uses `http://www.google.com`.

The webapp entry point is the `server.py` script.

By default, the web application will run on http://localhost:8080. To change it,
use `--host` and `--port` options for the `server.py` script.


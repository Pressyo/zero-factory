zeroFactory
===========

This is the zeroMQ app factory for Pressyo products. Multiple language is supported. Below are deployment instructions

# Python #
Good news everybody, you can actually install using pip! This is how you'd do it:

## Deploying without a build server ##
1. clone the git repo into local system
2. To install: `sudo pip install -e /path/to/zeroFactory/python/ZeroFactory-x.y.z.tar.gz`
3. To use: `from zeroFactory import appFactory`
4. Usage instructions can be found in the docs

## Deploying with a build server (or your own cheeseshop) ##
1. clone the git repo into the build server
2. Navigate to `/path/to/zeroFactory/python`
3. Run `python setup.py sdist`
4. Register your app with your own cheeseshop: see [Tarek Ziade's excellent guide](http://ziade.org/2008/03/20/how-to-run-your-own-private-pypi-cheeseshop-server/). You're on your own if you use Chishop instead
5. To install on slave servers: `pip install zeroFactory -i http://cheeseshop.workfloo.com`
6. Usage instructions can be found in the docs.


# Javascript (node.js) #
... stuff here ..


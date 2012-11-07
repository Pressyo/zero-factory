zero factory
===========

This is the zeroMQ app factory for Pressyo products. Multiple language is supported. Below are deployment instructions

# Python #

## Requirements ##
gevent is now a required package. gevent 1.0rc1 is recommended. 

Due to the fact that gevent 1.0 is yet to be in the PyPI, you have to manually install it first:

1. Install libev4: ` sudo apt-get install libev4 libev-libevent-dev `
2. Download the latest version of gevent (gevent-1.0rc1): ` wget https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc1.tar.gz `
3. Untar it: `tar -xzvf gevent-1.0rc1.tar.gz`
4. Go to the untar'd directory, then make: `python setup.py build`
5. Install it (sudo may be required): `python setup.py install`

## Installing zero-factory ##
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


import sys
import os

# fix import and weird WSGI path issues
abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
parentdir = os.path.dirname(abspath)
sys.path.insert(1, parentdir)  # add current path
os.chdir(abspath)

from zeroFactory import appFactory

# define self module first
currentModule = sys.modules[__name__]

# define routes
routes = {
		'create': 'createFunc',
		'retrieve': 'retrieveFunc',
		'update': 'updateFunc',
		'delete': 'deleteFunc'
		}

address = 'tcp://*:1234'

def main():
    app = appFactory.App(routes=routes, currentModule=currentModule,
                         bind=address, socketType='rep')
    app.run()


if __name__ == "__main__":
    main()
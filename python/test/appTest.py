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
		}

address = 'tcp://*:1234'

socketType = sys.argv[1]
if socketType not in ['pull', 'rep']:
	raise TypeError('wrong socket type')

def createFunc(params):
	d = appFactory.SUCCESSMESSAGE
	print params
	d['result'] = 'createdFunction!'
	return d

def main():
    app = appFactory.App(routes=routes, currentModule=currentModule,
                         bind=address, socketType=socketType)
    app.run()


if __name__ == "__main__":
    main()
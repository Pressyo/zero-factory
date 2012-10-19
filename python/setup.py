from distutils.core import setup


setup(
    name='ZeroFactory',
    version='0.1.0',
    author='Xuanyi Chew',
    author_email='chewxy@gmail.com',
    packages=['zeroFactory', 'test'],
    license='LICENSE.txt',
    description='App factory for zeroMQ apps',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyzmq == 2.2.0",
        "msgpack-python == 0.2.2"
    ],
)
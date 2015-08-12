set -e # exit on first error
set -x # print commands

DEV="0"
while getopts ":v" OPTION
do
        case $OPTION in
                v)
                        DEV="1"
        esac
done

echo "updating all the things"
sudo apt-get -qq update -y

if [ $DEV = "1" ]
then
        echo "Vagrant version. Not upgrading for now"
        homepath='/home/vagrant'
else
        sudo apt-get -qq upgrade -y
        homepath=~
fi



echo "Deploying Magic!"
echo "Setting locale"
sudo locale-gen en_AU.UTF-8

echo "Installing dependencies"
echo "Installing Build Dependencies"
sudo apt-get -qq install -y build-essential python-dev python-pip git git-core python-software-properties automake autoconf libtool
echo "Installing zeroMQ build dependencies"
sudo apt-get -qq install -y uuid-dev e2fsprogs
echo "Installing gevent build dependencies"
sudo apt-get -qq install -y libev4 libev-libevent-dev

echo "creating src"

mkdir -p $homepath/src


echo "installing zeroMQ"
cd $homepath/src
wget -q http://download.zeromq.org/zeromq-4.0.3.tar.gz
tar -xzvf zeromq-4.0.3.tar.gz
cd zeromq-4.0.3
./configure && make && sudo make install
sudo ldconfig

echo "installing gevent"
cd $homepath/src
pip install cython git+git://github.com/surfly/gevent.git#egg=gevent

echo "Vagrant version. No RSA key needed. Installing PIP requirements instead"
cd /vagrant/deploy
sudo pip install -r requirements.txt


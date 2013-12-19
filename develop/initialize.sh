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
#echo "Installing couchdb dependencies"
#sudo apt-get -qq install -y erlang libicu-dev libmozjs-dev libcurl4-openssl-dev erlang-nox erlang-dev erlang-manpages erlang-base-hipe erlang-eunit erlang-xmerl erlang-inets


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

echo "adding PPAs"
sudo add-apt-repository ppa:rwky/redis -y
sudo add-apt-repository ppa:nginx/stable -y
# sudo add-apt-repository ppa:uwsgi/release -y

echo "updating"
sudo apt-get -qq update -y

echo "installing redis"
sudo apt-get -qq install redis-server -y

echo "installing nginx"

sudo apt-get -qq install nginx -y

echo "installing uwsgi"
sudo apt-get -qq install uwsgi uwsgi-plugin-python -y


#echo "intalling CouchDB"
#cd $homepath/src
#wget -q http://mirror.ventraip.net.au/apache/couchdb/source/1.3.0/apache-couchdb-1.3.0.tar.gz
#tar -xzvf apache-couchdb-1.3.0.tar.gz
#cd apache-couchdb-1.3.0
#./configure
#make && sudo make install

#echo "configuring CouchDB Now"
#sudo adduser --system --home /usr/local/var/lib/couchdb --no-create-home --shell /bin/bash --group --gecos "CouchDB" couchdb
#sudo chown -R couchdb:couchdb /usr/local/etc/couchdb
#sudo chown -R couchdb:couchdb /usr/local/var/lib/couchdb
#sudo chown -R couchdb:couchdb /usr/local/var/log/couchdb
#sudo chown -R couchdb:couchdb /usr/local/var/run/couchdb

#sudo chmod -R 0770 /usr/local/etc/couchdb
#sudo chmod -R 0770 /usr/local/var/lib/couchdb
#sudo chmod -R 0770 /usr/local/var/log/couchdb
#sudo chmod -R 0770 /usr/local/var/run/couchdb

#echo "CouchDB Log Rotation Config"
#sudo ln -s /usr/local/etc/logrotate.d/couchdb /etc/logrotate.d/couchdb

#echo "Starting CouchDB service"
#sudo /usr/local/etc/init.d/couchdb start

if [ $DEV = "1" ]
then
        echo "Vagrant version. No RSA key needed. Installing PIP requirements instead"
        cd /vagrant/deploy
        sudo pip install -r requirements.txt
else
        cd $homepath/.ssh
        mkdir key_backup
        cp id_rsa* key_backup
        rm id_rsa*
        ssh-keygen -t rsa -C "admin@pressyo.com"

        echo "YOU SHOULD COPY THIS NOW"
        cat $homepath/.ssh/id_rsa.pub

fi

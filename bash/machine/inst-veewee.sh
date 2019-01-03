#! /bin/bash

sudo apt-get install libxslt1-dev libxml2-dev zlib1g-dev libcurl4-openssl-dev -y
rvm install 2.5.1
( cd ; git clone https://github.com/jedi4ever/veewee.git ; cd veewee ; rvm use ruby@veewee --create ; gem install bundler ; bundle install )
VBOX_VERSION=echo $(dpkg -s virtualbox | egrep -o -m 1 '[0-9]{1}\.[0-9]{1}\.[0-9]{2}')
GUEST_ADDITIONS_URL="http://download.virtualbox.org/virtualbox/$VBOX_VERSION/"
curl -O $GUEST_ADDITIONS_URL


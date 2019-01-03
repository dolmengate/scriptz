#! /bin/bash

sudo apt-add-repository -y ppa:rael-gc/rvm 
sudo apt-get update 
sudo apt-get install rvm 
sudo useradd -G rvm $(whoami)
echo ". /etc/profile.d/rvm.sh" >> ~/.bashrc
echo "RVM installed, you must logout and log back in to use RVM"


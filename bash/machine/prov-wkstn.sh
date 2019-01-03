#! /bin/bash

echo "--- Application Prerequisites"
sudo apt-get install openjdk-8-jdk-headless openjdk-11-jdk-headless -y

echo "--- Development Tools"
echo "Installing IntelliJ Community"
sudo bash ./inst-intellij.sh
echo "Installing Sublime Text 3"
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text -y
echo "Installing Docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce -y
echo "Installing Jenkins"
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo echo "deb https://pkg.jenkins.io/debian-stable binary/" >> /etc/apt/sources.list
sudo apt-get update
sudo apt-get install jenkins -y
echo "Installing VirtualBox"
sudo apt-get install virtualbox -y
echo "Installing Vagrant"
sudo apt-get install vagrant -y
echo "Installing vagrant plugins"
vagrant plugin install winrm
vagrant plugin install winrm-fs


echo "--- Display Settings"
echo "Installing i3"
sudo apt-get update
sudo apt-get install i3 xbacklight alsa-utils pulseaudio -y
sudo ubuntu-drivers autoinstall
sudo cp ./i3/grub /etc/default/grub
sudo update-grub
sudo cp ./i3/config ~/.config/i3/
sudo systemctl restart display-manager


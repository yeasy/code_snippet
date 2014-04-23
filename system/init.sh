#!/bin/sh
#Please run this script with root privilege

release='saucy'
user='baohua'

sudo echo 'baohua ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


sudo apt-add-repository ppa:apt-fast/stable -y

sudo aptitude update;
sudo dpkg --set-selections < package.list && sudo aptitude upgrade

cp -f ./.bash* /home/${user}/

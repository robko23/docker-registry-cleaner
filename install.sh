#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if ! command -v docker &> /dev/null
then
    echo 'Command `docker` could not be found'
    exit
fi

while true; do
    read -p "Have you edited main.py? The program will install as is when you answer" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "Creating user"

useradd --system registry-cleaner -m -d /var/lib/registry-cleaner
usermod -aG docker registry-cleaner

echo "Copying files"
mkdir -p /var/lib/registry-cleaner
cp ./regctl /var/lib/registry-cleaner
cp ./main.py /var/lib/registry-cleaner
chown -R root:docker /var/lib/registry-cleaner
chmod -R 775 /var/lib/registry-cleaner

echo "Installing service"
cp ./registry-cleaner.timer /etc/systemd/system
cp ./registry-cleaner.service /etc/systemd/system

echo "Enabling timer"
systemctl daemon-reload
systemctl enable registry-cleaner.timer
systemctl start registry-cleaner.timer

echo "Setting up registry connection"
read -p "Enter registry url: " registry_url
read -p "Username: " username
read -sp "Password: " password

sudo -u registry-cleaner /var/lib/registry-cleaner/regctl registry login $registry_url -u $username -p $password

echo "Done"

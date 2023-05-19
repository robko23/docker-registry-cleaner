#!/bin/bash
while true; do
    read -p "Are you sure you want to uninstall?" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

echo "Disabling service"
systemctl disable registry-cleaner.timer

echo "Removing service"
rm /etc/systemd/system/registry-cleaner.service
rm /etc/systemd/system/registry-cleaner.timer

echo "Removing user"
userdel -rf registry-cleaner

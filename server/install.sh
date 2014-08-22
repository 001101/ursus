#!/bin/bash


sudo apt-get -y install apache2 libapache2-mod-wsgi python-pip git sqlite3
sudo pip install flask flask-sqlalchemy flask-restless requests
git clone https://github.com/Ch00k/ursus.git
sudo mkdir -p /var/www/ursus/assets
sudo cp ursus/client/result_processor.py /var/www/ursus/assets/
sudo cp ursus/server/benchmarks/*.job /var/www/ursus/assets/
sudo rm -rf /etc/apache2/sites-enabled/000-default
sudo cp ursus/server/ursus.vhost /etc/apache2/sites-enabled/
sudo cp ursus/server/ursus.wsgi /var/www/ursus/
sudo chown -R www-data:www-data /var/www/ursus
sudo cp ursus/server/server.py /var/www/ursus/
sudo service apache2 restart

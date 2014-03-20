#!/bin/bash
set -e

floating_ip=`curl http://169.254.169.254/latest/meta-data/public-ipv4`

echo "Configuring Hosts and SSH host checking..."
# Skip ssh new host check.
cat<<EOF | sudo tee ~/.ssh/config
Host github.com
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  User ubuntu
EOF

echo "Adding docker repository"
sudo sh -c "echo deb http://get.docker.io/ubuntu docker main\
   > /etc/apt/sources.list.d/docker.list"

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9

# Install the necessary packages.
echo "Updating apt repository..."
sudo apt-get update -qq

echo "Installing base packages..."
sudo apt-get install -y -qq git python python-dev python-pip libssl-dev \
   lxc-docker apache2 libapache2-mod-wsgi apache2-mpm-prefork apache2-utils \
   libexpat1 ssl-cert lxc-docker cgroup-lite

echo "Creating SSH key..."
ssh-keygen -t rsa -N "" -f /home/ubuntu/.ssh/id_rsa -y
pubkey=`cat /home/ubuntu/.ssh/id_rsa.pub`

echo "Cloning cnc-grader repository..."
if [ ! -d cnc-grader ]; then
   git clone -q git@github.com:mgius/cnc-grader.git
else
   pushd cnc-grader
   git pull
   popd
fi

echo "Installing dependencies from PyPI (this may take some time)..."
sudo pip install -q -r ~/cnc-grader/requirements.txt

echo "granting ubuntu user access to docker socket"
sudo usermod -a -G docker ubuntu
sudo service docker restart

cd ~/cnc-grader

./build_docker.sh

echo "Installing application schema..."
python ./manage.py syncdb --noinput
chown ubuntu:www-data db.sqlite3
chmod g+rw db.sqlite3

echo "Configuring Webserver..."
sudo mkdir -p /var/python/eggs
sudo mkdir -p /var/log/apache

sudo a2enmod ssl
sudo mkdir -p /etc/apache2/ssl

sudo rm /etc/apache2/sites-enabled/000-default
sudo ln -s /home/ubuntu/cnc-grader/apache.conf /etc/apache2/sites-enabled/000-default

sudo openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/ST=CA/L=Mountain View/O=Nebula Inc/CN=cnc-grader.markgius.com" -keyout /etc/apache2/ssl/apache.key -out /etc/apache2/ssl/apache.crt

sudo chown -R ubuntu:www-data /home/ubuntu/cnc-grader
sudo chown -R ubuntu:www-data /var/python/eggs
sudo chown -R ubuntu:www-data /var/log/apache
sudo mkdir /var/www/submissions
sudo chown -R ubuntu:www-data /var/www/submissions
sudo chmod ug+rwx /var/www/submissions

sudo service apache2 restart

docker ps -a | grep -q "redis" || docker run -d dockerfiles/redis 

exit 0

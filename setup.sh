sudo apt update
sudo apt -y upgrade

sudo apt -y install nginx
sudo ufw allow 'Nginx Full'

if [ ! -e /etc/nginx/sites-available/server.conf ]
then
    sudo cp ./server.conf /etc/nginx/sites-available
    sudo ln -s /etc/nginx/sites-available/server.conf /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default
fi
sudo systemctl restart nginx

sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot

if [ ! -e /usr/bin/certbot ]
then
    sudo ln -s /snap/bin/certbot /usr/bin/certbot
fi
sudo certbot --nginx --config cert_cli.ini
sudo ufw allow 'Nginx HTTPS'

if ! command -v redis-server &> /dev/null
then
    sudo apt -y install make
    sudo apt -y install tcl
    cd
    wget http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    cd redis-stable
    make
    sudo make install
    sudo sh -c 'echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf'
    sudo sysctl vm.overcommit_memory=1
fi

IP=$(dig @resolver4.opendns.com myip.opendns.com +short)
mkdir -p ~/parsagon
cd ~/parsagon

sudo apt update
sudo apt -y upgrade

if [ ! -e /usr/local/bin/mkcert ]
then
    sudo apt -y install libnss3-tools
    sudo apt -y install golang-go
    git clone https://github.com/FiloSottile/mkcert && cd mkcert
    go build -ldflags "-X main.Version=$(git describe --tags)"
    sudo cp mkcert /usr/local/bin/mkcert
    sudo chmod +x /usr/local/bin/mkcert
fi
mkcert -cert-file ~/parsagon/cert.pem -key-file ~/parsagon/key.pem $IP

sudo apt -y install nginx
sudo ufw allow 'Nginx HTTPS'

if [ ! -e /etc/nginx/sites-available/server.conf ]
then
    sudo cp ./server.conf /etc/nginx/sites-available
    sudo ln -s /etc/nginx/sites-available/server.conf /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default
fi
sudo systemctl restart nginx
cd -

#if ! command -v redis-server &> /dev/null
#then
    #sudo apt -y install make
    #sudo apt -y install tcl
    #cd
    #wget http://download.redis.io/redis-stable.tar.gz
    #tar xvzf redis-stable.tar.gz
    #cd redis-stable
    #make
    #sudo make install
    #sudo sh -c 'echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf'
    #sudo sysctl vm.overcommit_memory=1
#fi

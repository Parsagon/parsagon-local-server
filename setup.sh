ORIG_DIR=$PWD
IP_ADDR=$(dig @resolver4.opendns.com myip.opendns.com +short)

sudo apt update
sudo apt -y upgrade

sudo apt -y install python3-pip
sudo apt -y install daphne
pip install -r server/requirements.txt

if ! command -v mkcert &> /dev/null
then
    cd ~/parsagon
    mkdir -p ~/parsagon
    sudo apt -y install libnss3-tools
    sudo apt -y install golang-go
    git clone https://github.com/FiloSottile/mkcert && cd mkcert
    go build -ldflags "-X main.Version=$(git describe --tags)"
    sudo cp mkcert /usr/local/bin/mkcert
    sudo chmod +x /usr/local/bin/mkcert
fi
mkcert -cert-file ~/parsagon/cert.pem -key-file ~/parsagon/key.pem $IP_ADDR

sudo apt -y install nginx
sudo ufw allow 'Nginx HTTPS'

cd $ORIG_DIR
sudo cp ./server.conf /etc/nginx/sites-available
sudo ln -s /etc/nginx/sites-available/server.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

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

sudo apt -y install supervisor
cd $ORIG_DIR
sudo cp supervisor.conf /etc/supervisor/conf.d/
sudo supervisorctl stop all
sudo supervisorctl update
sudo supervisorctl start all

cd $ORIG_DIR

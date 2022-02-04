SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
IP_ADDR=$(dig @resolver4.opendns.com myip.opendns.com +short)

mkdir -p ~/parsagon
cp -r ./server/ ~/parsagon/
cd ~/parsagon/server
printf '%s\n%s\n' "export API_KEY=$1" "$(cat daphne.sh)" > daphne.sh
printf '%s\n%s\n' "export API_KEY=$1" "$(cat celery.sh)" > celery.sh
cd $SCRIPT_DIR

sudo apt update
sudo apt -y upgrade

sudo apt -y install redis-server
sudo cp ./redis.conf /etc/redis/redis.conf
sudo systemctl restart redis.service

#sudo apt -y install python3-pip
sudo apt -y install python3-venv
python3 -m venv ~/parsagon/venv
source ~/parsagon/venv/bin/activate

sudo apt -y install daphne
pip install -r server/requirements.txt

if ! command -v mkcert &> /dev/null
then
    cd ~/parsagon
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

cd $SCRIPT_DIR
sudo cp ./nginx.conf /etc/nginx/sites-available
sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

sudo apt -y install supervisor
cd $SCRIPT_DIR
sudo cp supervisor.conf /etc/supervisor/conf.d/
sudo supervisorctl stop all
sudo supervisorctl update
sudo supervisorctl start all

cd $SCRIPT_DIR

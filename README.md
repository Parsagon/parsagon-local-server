# parsagon-local-server

To install on Ubuntu 20:
```
sudo apt update
sudo apt install python3-pip
sudo apt install python3-venv

python3 -m venv parsagon-venv
source parsagon-venv/bin/activate
pip install parsagon
parsagon-server <paste your api_key here>
```

For development:
Make sure to include the test server as a second argument to parsagon-server:
`parsagon-server <api_key> <test_server>`

To add a proxy:
Edit /etc/tinyproxy/tinyproxy.conf to point to your proxy, then run:
`sudo service tinyproxy restart`
and add
`PROXY=127.0.0.1:8888` to `daphne.sh`.

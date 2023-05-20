#!/bin/bash

set -e
echo "Starting deployment"

cd /opt/dvmn-star-burger

git pull origin master

if ls venv
then
echo "venv already exists"
else
echo "There is no venv"
python3 -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt

apt install nodejs
apt install npm

npm ci --dev

python3 manage.py collectstatic --noinput
python3 manage.py migrate

systemctl restart starburger-django

echo "Deployed successfully"

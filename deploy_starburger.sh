#!/bin/bash

set -e
echo "Starting deployment"

cd /opt/dvmn-star-burger

git add .
git commit -m "Save changes before redeployment"
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

npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

systemctl restart starburger-django

TOKEN=$(cat .env | grep ROLLBAR_ACCESS_TOKEN | cut -d'=' -f 2)
ROLLBARENV=$(cat .env | grep ROLLBAR_ENVIRONMENT | cut -d'=' -f 2)
COMMIT=$(git rev-parse HEAD)
COMMENT=$(git log -1 --pretty=format:%B)

JSON=$(jq -n \
--arg env "$ROLLBARENV" \
--arg hash "$COMMIT" \
--arg name "$(whoami)" \
--arg comment "$COMMENT" \
'{"environment": $env, "revision": $hash, "local_username": $name, "comment": $comment}'
)

curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --header 'X-Rollbar-Access-Token: '$TOKEN \
     --data "$JSON"

echo "Deployed successfully"

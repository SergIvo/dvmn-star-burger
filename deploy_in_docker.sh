#!/bin/bash

set -e
echo "Starting deployment"

cd /opt/dvmn-star-burger

git add .
git commit -m "Save changes before redeployment"
git pull origin master

docker-compose up --build -d

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

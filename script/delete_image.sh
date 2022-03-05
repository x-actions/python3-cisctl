#!/bin/bash

login_data() {
cat <<EOF
{
  "username": "$USERNAME",
  "password": "$PASSWORD"
}
EOF
}

TOKEN=`curl -s -H "Content-Type: application/json" -X POST -d "$(login_data)" "https://hub.docker.com/v2/users/login/" | jq -r .token`
echo $TOKEN
set -x

delete_image() {
  local org=$1
  local name=$2
  curl "https://hub.docker.com/v2/repositories/${org}/${name}/" \
    -X DELETE -H "Authorization: JWT ${TOKEN}"
  echo 'delete image ${org}/${name}'
}

delete_tag() {
  local org=$1
  local name=$2
  for i in $(skopeo list-tags docker://${org}/${name} | jq -c '.Tags|join(";")' | xargs echo | tr ";" "\n"); do
    curl "https://hub.docker.com/v2/repositories/${org}/${name}/tags/${i}/" \
      -X DELETE \
      -H "Authorization: JWT ${TOKEN}"
    echo 'delete image tag ${org}/${name}:${i}'
  done
}

for i in $(cat $2); do
  delete_tag $1 $i
  delete_image $1 $i
done

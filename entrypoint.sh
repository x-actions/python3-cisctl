#!/bin/bash
set -e

export DEST_TRANSPORT_USER=${DEST_TRANSPORT_USER:-"xiexianbin"}
export DEST_TRANSPORT_PASSWORD=${DEST_TRANSPORT_PASSWORD:-"xiexianbin"}
export GIT_TOKEN=${GIT_TOKEN}
export GIT_ORG=${GIT_ORG}
export GIT_REPO=${GIT_REPO}
export SRC_IMAGE_LIST_URL=${SRC_IMAGE_LIST_URL}
export DEST_REPO=${DEST_REPO}
export SRC_TRANSPORT=${SRC_TRANSPORT}
export DEST_TRANSPORT=${DEST_TRANSPORT}
export THREAD_POOL_NUM=${THREAD_POOL_NUM:-2}
export LOG_LEVEL=${LOG_LEVEL:-"DEBUG"}

echo "## Check Package Version ##################"
bash --version
git version
skopeo --version

echo "## Login dest TRANSPORT ##################"
set -x
skopeo login -u ${DEST_TRANSPORT_USER} -p ${DEST_TRANSPORT_PASSWORD} ${DEST_REPO/\/*/}

cisctl

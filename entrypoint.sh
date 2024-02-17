#!/bin/bash
set -e

export GIT_TOKEN=${GIT_TOKEN}
export GIT_ORG=${GIT_ORG}
export GIT_REPO=${GIT_REPO}

echo "## Check Package Version ##################"
bash --version
git version
skopeo --version

echo "## Login dest TRANSPORT ##################"
set -x
skopeo login \
  -u ${DEST_TRANSPORT_USER:-"xiexianbin"} \
  -p ${DEST_TRANSPORT_PASSWORD:-"xiexianbin"} \
  ${DEST_REPO/\/*/}

cisctl sync \
  --src-transport "${SRC_TRANSPORT}" \
  --dest-transport "${DEST_TRANSPORT}" \
  --git-repo "${GIT_REPO}" \
  --thread-pool-size ${THREAD_POOL_NUM:-2} \
  --dest-repo "${DEST_REPO}" \
  --job-batch-size ${JOB_BATCH_COUNT:-3} \
  --src-image-list-url "${SRC_IMAGE_LIST_URL}" \
  --after-timeuploadedms "${AFTER_TIMEUPLOADEDMS:-0}" \
  --debug

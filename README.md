# Container Images Sync

github actions for [Container Images Sync](https://github.com/marketplace/actions/container-images-sync)

## Environment Variables

- GIT_ORG: github org
- GIT_REPO: github repo
- GIT_TOKEN: github token
- SRC_IMAGE_LIST_URL: SRC_IMAGE_LIST_URL, default: "https://raw.githubusercontent.com/x-mirrors/gcr.io/main/google-containers.txt"
- DEST_REPO: DEST register REPO
- SRC_TRANSPORT: SRC TRANSPORT
- DEST_TRANSPORT: DEST TRANSPORT
- DEST_TRANSPORT_USER: user
- DEST_TRANSPORT_PASSWORD: "password"
- THREAD_POOL_NUM: sync thread pool num

## How to Use

```
    - name: Container Images Sync
      uses: x-actions/python3-cisctl@v1
      env:
        GIT_ORG: "x-mirrors"
        GIT_REPO: "gcr.io"
        GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SRC_IMAGE_LIST_URL: "https://raw.githubusercontent.com/x-mirrors/gcr.io/main/google-containers.txt"
        DEST_REPO: "docker.io/gcmirrors"
        SRC_TRANSPORT: "docker"
        DEST_TRANSPORT: "docker"
        DEST_TRANSPORT_USER: "user"
        DEST_TRANSPORT_PASSWORD: "password"
```

## ref

- install skopeo: https://www.xiexianbin.cn/container/tools/skopeo/
- local run

```
pip3 install -r requirements.txt
export GIT_ORG="x-mirrors"
export GIT_REPO="gcr.io"
export GIT_TOKEN='${{ secrets.GITHUB_TOKEN }}'
export SRC_IMAGE_LIST_URL="https://raw.githubusercontent.com/x-mirrors/gcr.io/main/ml-pipeline.txt"
export DEST_REPO="docker.io/mlmirrors"
export SRC_TRANSPORT="docker"
export DEST_TRANSPORT="docker"
export DEST_TRANSPORT_USER="xianbinxie"
export DEST_TRANSPORT_PASSWORD="<passwords>"
cisctl
```

- tests

```
python3 -m unittest cis.tests.unit.test_skopeo.SkopeoTestCase.test_do_sync
```

# Container Images Sync

[![PyPI-python3-cisctl](https://img.shields.io/pypi/v/python3-cisctl.svg?maxAge=3600)](https://pypi.org/project/python3-cisctl/)

Github Actions for [Container Images Sync](https://github.com/marketplace/actions/container-images-sync)

## How to Use by Github Actions

```
    - name: Container Images Sync
      uses: x-actions/python3-cisctl@v1.0.0
      env:
        GIT_ORG: "x-mirrors"
        GIT_REPO: "gcr.io"
        GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SRC_IMAGE_LIST_URL: "https://raw.githubusercontent.com/x-mirrors/gcr.io/main/k8s.txt"
        DEST_REPO: "docker.io/gcmirrors"
        SRC_TRANSPORT: "docker"
        DEST_TRANSPORT: "docker"
        DEST_TRANSPORT_USER: "user"
        DEST_TRANSPORT_PASSWORD: "password"
```

Environment Variables:

- GIT_ORG: github org
- GIT_REPO: github repo
- GIT_TOKEN: github token
- SRC_IMAGE_LIST_URL: SRC_IMAGE_LIST_URL, default: "https://raw.githubusercontent.com/x-mirrors/gcr.io/main/k8s.txt"
- DEST_REPO: DEST register REPO
- SRC_TRANSPORT: SRC TRANSPORT
- DEST_TRANSPORT: DEST TRANSPORT
- DEST_TRANSPORT_USER: user
- DEST_TRANSPORT_PASSWORD: "password"
- THREAD_POOL_NUM: sync thread pool num

## Dev and Test

- local run

```
# install
pip3 install -r requirements.txt
python3 setup.py install
# or
pip3 install python3-cisctl

# set env
export GIT_ORG="x-mirrors"
export GIT_REPO="gcr.io"
export GIT_TOKEN='${{ secrets.GITHUB_TOKEN }}'
export SRC_IMAGE_LIST_URL="https://raw.githubusercontent.com/x-mirrors/gcr.io/main/k8s.txt"
export DEST_REPO="docker.io/gcmirrors"
export SRC_TRANSPORT="docker"
export DEST_TRANSPORT="docker"
export DEST_TRANSPORT_USER="xianbinxie"
export DEST_TRANSPORT_PASSWORD="<passwords>"

# run sync
cisctl
```

- tests

```
python3 -m unittest cisctl.tests.unit.test_skopeo.SkopeoTestCase.test_do_sync
```

## ref

- [install skopeo](https://www.xiexianbin.cn/container/tools/skopeo/)
- replace old tools [x-mirrors/gcmirrors](https://github.com/x-mirrors/gcmirrors)

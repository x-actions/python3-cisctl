# create by xiexianbin, Container Images Sync
FROM ubuntu:22.04

# Dockerfile build cache
ENV REFRESHED_AT 2022-02-01

LABEL "com.github.actions.name"="Container Images Sync"
LABEL "com.github.actions.description"="Container Images Sync"
LABEL "com.github.actions.icon"="repeat"
LABEL "com.github.actions.color"="blue"
LABEL "repository"="http://github.com/x-actions/python3-cisctl"
LABEL "homepage"="http://github.com/x-actions/python3-cisctl"
LABEL "maintainer"="xiexianbin<me@xiexianbin.cn>"

LABEL "Name"="Container Images Sync"
LABEL "Version"="2.0.0"

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# apt install -y docker-ce docker-ce-cli containerd.io systemctl start docker
RUN apt update && \
    apt install -y git python3 python3-pip jq wget && \
    # install skopeo
    apt install libgpgme-dev libassuan-dev libbtrfs-dev libdevmapper-dev pkg-config golang-1.20 -y && \
    ln -s /usr/lib/go-1.20/bin/go /usr/bin/go && \
    export GOPATH=/gopath && \
    mkdir -p $GOPATH/src/github.com/containers && \
    wget -O skopeo-1.14.2.tar.gz https://github.com/containers/skopeo/archive/refs/tags/v1.14.2.tar.gz && \
    tar -zxvf skopeo-1.14.2.tar.gz -C $GOPATH/src/github.com/containers/ && \
    cd $GOPATH/src/github.com/containers && \
    mv skopeo-1.14.2 skopeo && \
    cd skopeo && \
    DISABLE_DOCS=1 make bin/skopeo && \
    mv bin/skopeo /usr/local/bin/ && \
    # install gcrane
    wget https://github.com/google/go-containerregistry/releases/download/v0.16.1/go-containerregistry_Linux_x86_64.tar.gz && \
    tar -zxvf go-containerregistry_Linux_x86_64.tar.gz && \
    rm go-containerregistry_Linux_x86_64.tar.gz && \
    mv gcrane /usr/local/bin/ && \
    # install python3-cisctl
    git clone https://github.com/x-actions/python3-cisctl.git -b v2 && \
    cd python3-cisctl && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

ADD entrypoint.sh /
RUN chmod +x /entrypoint.sh

WORKDIR /github/workspace
ENTRYPOINT ["/entrypoint.sh"]

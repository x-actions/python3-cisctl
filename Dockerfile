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
LABEL "Version"="1.2.1"

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# apt install -y docker-ce docker-ce-cli containerd.io systemctl start docker
RUN apt update && \
    apt install -y git python3 python3-pip skopeo jq wget && \
    wget https://github.com/google/go-containerregistry/releases/download/v0.16.1/go-containerregistry_Linux_x86_64.tar.gz && \
    tar -zxvf go-containerregistry_Linux_x86_64.tar.gz && \
    rm go-containerregistry_Linux_x86_64.tar.gz && \
    mv gcrane /usr/local/bin/ && \
    git clone https://github.com/x-actions/python3-cisctl.git && \
    cd python3-cisctl && \
    python3 setup.py install

ADD entrypoint.sh /
RUN chmod +x /entrypoint.sh

WORKDIR /github/workspace
ENTRYPOINT ["/entrypoint.sh"]

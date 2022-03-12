# create by xiexianbin, Container Images Sync
FROM ubuntu:20.04

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
LABEL "Version"="1.0.0"

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# apt install -y docker-ce docker-ce-cli containerd.io systemctl start docker
RUN apt update && \
    apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    . /etc/os-release && \
    echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
    curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key | apt-key add - && \
    apt update && \
    apt install -y git python3 python3-pip skopeo jq && \
    cd ~ && \
    git clone https://github.com/x-actions/python3-cisctl.git && \
    cd python3-cisctl && \
    pip3 install -r requirements.txt && \
    python3 setup.py --version && \
    python3 setup.py install
# line:35 # git checkout v1 && \

ADD entrypoint.sh /
RUN chmod +x /entrypoint.sh

WORKDIR /github/workspace
ENTRYPOINT ["/entrypoint.sh"]

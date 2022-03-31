# Copyright 2022 xiexianbin.cn
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""python skopeo utils."""

import json

from cisctl.bash import Bash


class Skopeo(object):

    def __init__(self):
        self.bash = Bash()

    def copy(self, src_repo, dest_repo, name, tag, dest_name=None, src_transport='docker', dest_transport='docker',
             src_tls_verify='false', dest_tls_verify='false'):
        """ Copy an IMAGE-NAME from one location to another

        :param src_repo: k8s.gcr.io
        :param dest_repo: docker.io/gcmirrors
        :param name: pause-amd64
        :param tag: latest
        :param dest_name: default list name
        :param src_transport: docker
        :param dest_transport: docker
        :param src_tls_verify: false
        :param dest_tls_verify: false

        skopeo copy --insecure-policy --src-tls-verify=false --dest-tls-verify=false -q \
        docker://k8s.gcr.io/pause-amd64:latest docker://docker.io/gcmirrors/pause-amd64:latest
        :return:
        """
        if dest_name is None:
            dest_name = name
        cmd = f'skopeo copy --insecure-policy --src-tls-verify={src_tls_verify} --dest-tls-verify={dest_tls_verify} ' \
              f'-q {src_transport}://{src_repo}/{name}:{tag} {dest_transport}://{dest_repo}/{dest_name}:{tag}'
        _ = self.bash.run(cmd)

    def sync(self, src_repo, dest_repo, name, src_transport='docker', dest_transport='docker',
             src_tls_verify='false', dest_tls_verify='false'):
        """ Synchronize one or more images from one location to another

        :param src_repo: k8s.gcr.io
        :param dest_repo: docker.io/gcmirrors
        :param name: pause-amd64
        :param src_transport: docker
        :param dest_transport: docker
        :param src_tls_verify: false
        :param dest_tls_verify: false

        skopeo sync --insecure-policy --src-tls-verify=false --dest-tls-verify=false --src docker --dest docker \
        k8s.gcr.io/pause-amd64 docker.io/gcmirrors
        :return:
        """
        cmd = f'skopeo sync --insecure-policy --src-tls-verify={src_tls_verify} --dest-tls-verify={dest_tls_verify} ' \
              f'--src {src_transport} --dest {dest_transport} {src_repo}/{name} {dest_repo}'
        _ = self.bash.run(cmd)

    def list_tags(self, transport, repo, name) -> {}:
        """ List tags in the transport/repository specified by the REPOSITORY-NAME

        :param transport: docker
        :param repo: k8s.gcr.io or quay.io/metallb
        :param name: pause-amd64

        skopeo list-tags docker://k8s.gcr.io/pause-amd64 | jq -c
        :return: {"Repository":"k8s.gcr.io/pause-amd64","Tags":["0.0.16"]}
        """
        cmd = f'skopeo list-tags {transport}://{repo}/{name} | jq -c'
        code, stdout, stderr = self.bash.run(cmd, result=True)
        if code == 0 and stdout is not None:
            try:
                result = json.loads(stdout)
            except json.decoder.JSONDecodeError:
                result = {}
        else:
            result = {}

        return result

    def do_sync(self, src_repo, dest_repo, name, src_transport='docker', dest_transport='docker'):
        """ Calculate src and dest repo tags difference set and sync

        :param src_repo: k8s.gcr.io
        :param dest_repo: docker.io/gcmirrors
        :param name: pause-amd64
        :param src_transport: docker
        :param dest_transport: docker
        :return:
        """
        src_tags = self.list_tags(transport=src_transport, repo=src_repo, name=name).get('Tags', [])
        dest_tags = self.list_tags(transport=dest_transport, repo=dest_repo, name=name).get('Tags', [])

        # full tags sync
        if len(dest_tags) == 0:
            self.sync(
                src_repo=src_repo,
                dest_repo=dest_repo,
                name=name,
                src_transport=src_transport,
                dest_transport=dest_transport)

        # difference tags set sync
        else:
            diff_tags = []
            for tag in src_tags:
                if tag not in dest_tags:
                    diff_tags.append(tag)

            for tag in diff_tags:
                self.copy(
                    src_repo=src_repo,
                    dest_repo=dest_repo,
                    name=name,
                    tag=tag,
                    src_transport=src_transport,
                    dest_transport=dest_transport)

        return src_tags

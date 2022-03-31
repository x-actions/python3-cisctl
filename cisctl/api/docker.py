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

""" Docker Register API v2 """

from cisctl import http
from cisctl import utils
from cisctl.api import RegisterBaseAPIV2


class DockerV2(RegisterBaseAPIV2):

    def __init__(self, registry_url='https://registry.hub.docker.com'):
        super().__init__()
        self.base_url = f'{registry_url}/v2/repositories'

    def delete_image(self, name, digest) -> bool:
        """ delete image by tag
        ref:
          - https://docs.docker.com/registry/spec/api/#deleting-an-image

        :param name: gcmirrors/kube-apiserver
        :param digest: sha256:xxx
        return:
        """
        url = f'{self.base_url}/{name}/manifests/{digest}'
        return http.http_delete(url)

    def list_tags(self, name, n=10, next='') -> {}:  # noqa
        """ list special image tags
        e.g.
          curl https://registry.hub.docker.com/v2/repositories/gcmirrors/kube-apiserver/tags
        ref:
          - https://docs.docker.com/registry/spec/api/#listing-image-tags

        :param name: gcmirrors/kube-apiserver
        :param n: page size
        :param next: next tag
        return:
        {
            "count":564,
            "next":"https://registry.hub.docker.com/v2/repositories/gcmirrors/kube-apiserver/tags?page=2",
            "previous":null,
            "results":[
                {
                    "creator":111330,
                    "id":108907821,
                    "image_id":null,
                    "images":[
                        {
                            "architecture":"amd64",
                            "features":"",
                            "variant":null,
                            "digest":"sha256:c3557736f3b86cba3890d0aadbaffd7d6360336c85d7a8e03331c5581eeff42f",
                            "os":"linux",
                            "os_features":"",
                            "os_version":null,
                            "size":51074491,
                            "status":"inactive",
                            "last_pulled":"2020-10-22T12:31:06.436456Z",
                            "last_pushed":null
                        }
                    ],
                    "last_updated":"2020-07-16T07:29:28.81499Z",
                    "last_updater":111330,
                    "last_updater_username":"xianbinxie",
                    "name":"v1.18.7-rc.0",
                    "repository":9345555,
                    "full_size":51074491,
                    "v2":true,
                    "tag_status":"inactive",
                    "tag_last_pulled":"2020-10-22T12:31:06.436456Z",
                    "tag_last_pushed":"2020-07-16T07:29:28.81499Z"
                },
                ...
            ]
        }
        """
        url = f'{self.base_url}/{name}/tags?n={n}'
        if next:
            url += f'&url={url}'

        return http.http_get(url)

    def last_tag(self, name) -> (bool, str, int):
        """ get docker image last tag pushed millisecond timestamp

        :param name: gcmirrors/kube-apiserver
        :return (bool, digest)
        """
        if 'docker.io' in name:
            name = name.replace('docker.io/', '')
        result, resp = self.list_tags(name)
        if result:
            _tag_dict = {}
            for item in resp.get('results', []):
                _tag_dict[item['name']] = utils.date2timestamp(item['tag_last_pushed'])

            sort_tags = utils.sort_dict(_tag_dict)
            if len(sort_tags):
                tag, timestamp = sort_tags[0]
                return True, tag, timestamp
            else:
                return True, None, None

        return False, None, None

    def sort_tags(self, name) -> (bool, []):
        raise NotImplemented

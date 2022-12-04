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
from typing import Dict
from typing import List
from typing import Tuple

from cisctl import http
from cisctl import utils
from cisctl.api import RegisterBaseAPIV2


class DockerV2(RegisterBaseAPIV2):

    def __init__(self, registry_url='https://registry.hub.docker.com', cache_timeout=120):
        """
        :param registry_url: docker registry url
        :param cache_timeout: cached docker images response, default is 120 second
        """
        super().__init__()
        self.base_url = f'{registry_url}/v2/repositories'
        self.caches = dict()  # {"name": {"request_timestamp": 1, "result": True/False, "response": Any}}
        self.cache_timeout = cache_timeout

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
        # check cache
        if 'docker.io' in name:
            name = name.replace('docker.io/', '')
        c = self.caches.get(name)
        if c is not None:
            if c['request_timestamp'] + self.cache_timeout > utils.timestamp():
                return c['result'], c['response']
            else:
                self.caches.pop(name)

        # new request
        url = f'{self.base_url}/{name}/tags?n={n}'
        if next:
            url += f'&url={url}'

        result, response = http.http_get(url)
        self.caches[name] = {
            "request_timestamp": utils.timestamp(),
            "result": result,
            "response": response,
        }
        return result, response

    def last_tag(self, name, sort_tags: List[Tuple[str, int]] = None) -> (str, int):
        """ get docker image last tag pushed millisecond timestamp

        :param name: gcmirrors/kube-apiserver
        :param sort_tags: ref self.sort_tags()
        :return (bool, _last_tag, _last_timestamp)
        """
        if sort_tags is None:
            _, sort_tags, _ = self.sort_tags(name)
        if len(sort_tags):
            _last_tag, _last_timestamp = sort_tags[0]
            return _last_tag, _last_timestamp
        else:
            return None, None

    def sort_tags(self, name) -> (bool, List[Tuple[str, int]], Dict):
        result, resp = self.list_tags(name)
        if result:
            _tag_timestamp_dict = dict()
            _tag_digest_dict = dict()
            for item in resp.get('results', []):
                _tag_timestamp_dict[item['name']] = utils.date2timestamp(item['tag_last_pushed'])
                if item.get('digest') is not None:
                    _tag_digest_dict[item['name']] = item.get('digest')
                elif len(item.get('images', [])) > 0 and item.get('images')[0].get('digest') is not None:
                    _tag_digest_dict[item['name']] = item.get('images')[0].get('digest')

            sort_tags = utils.sort_dict(_tag_timestamp_dict)
            return True, sort_tags, _tag_digest_dict
        else:
            if type(resp) is dict:
                if 'message' in resp.keys() and 'object not found' in resp['message']:
                    # if image not in docker hub, respo is:
                    # {
                    #   "message": "object not found",
                    #   "errinfo": {
                    #     "namespace": "gcriodistroless",
                    #     "repository": "base-debian9"
                    #   }
                    # }
                    return True, [], {}

                # may be need check 429 Too Many Requests
            return False, [], {}

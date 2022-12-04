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

""" Google Container Register v2 """

import uuid
from typing import Dict
from typing import List
from typing import Tuple

from cisctl import http
from cisctl import utils
from cisctl.api import RegisterBaseAPIV2


class GoogleContainerRegisterV2(RegisterBaseAPIV2):

    def __init__(self, registry_url='https://gcr.io', project=None):
        super().__init__()
        if project:
            self.base_url = f'{registry_url}/v2/{project}'
        else:
            self.base_url = f'{registry_url}/v2'

    def list_tags(self, name, n=10, next='') -> {}:  # noqa
        """ list special image tags
        e.g.
          gcloud container images list-tags k8s.gcr.io/pause --log-http
          curl -vv -H "user-agent: google-cloud-sdk //containerregistry/client:gcloud.py gcloud/313.0.1 command/gcloud.container.images.list-tags invocation-id/104af80f714b4c01a820b7a7874232c7 environment/None environment-version/None interactive/False from-script/False python/2.7.17 term/xterm-256color (Macintosh; Intel Mac OS X 21.3.0)" https://k8s.gcr.io/v2/kube-apiserver/tags/list  # noqa
        ref:
          - https://cloud.google.com/sdk/gcloud/reference/container/images/list-tags#GCLOUD-WIDE-FLAGS

        :param name: kube-apiserver
        :return
            {
              "child": [],
              "manifest": {
                "sha256:01a65e3568c0e2fc8d2f33015c0d4565f59a73fc3e2d01ef9a26241569591994": {
                  "imageSizeBytes": "0",
                  "layerId": "",
                  "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
                  "tag": [
                    "v1.11.4-beta.0"
                  ],
                  "timeCreatedMs": "0",
                  "timeUploadedMs": "1583462038503"
                },
                ...
              },
              "name": "kube-apiserver",
              "tags": [
                "v1.11.4-beta.0",
                ...
              ]
            }
        """
        url = f'{self.base_url}/{name}/tags/list'
        user_agent = \
            f'google-cloud-sdk //containerregistry/client:gcloud.py gcloud/313.0.1 ' \
            f'command/gcloud.container.images.list-tags invocation-id/{uuid.uuid4().hex} ' \
            f'environment/None environment-version/None interactive/False from-script/False ' \
            f'python/2.7.17 term/xterm-256color (Macintosh; Intel Mac OS X 21.3.0)'
        headers = {
            'Content-Type': 'application/json',
            'user-agent': user_agent
        }

        return http.http_get(url, None, headers)

    def sort_tags(self, name) -> (bool, List[Tuple[str, int]], Dict):
        """ sort image tags dict to Z-A

        :param name: kube-apiserver or ml-pipeline/api-server
        return:
        """
        result, resp = self.list_tags(name)
        if result:
            _tag_timestamp_dict = {}
            _tag_digest_dict = {}
            for digest, v in resp.get('manifest', {}).items():
                # digest like 'sha256:00c4c4b8cb7f747faff553ce447fbd86c7f062d04353c665c4087ef443aab8b5'
                for tag_name in v['tag']:
                    # tag like sha256-7939f3c6366155e73cb5025fc1fde5bd70c350cc9cd6b505340f7db8af655832.sbom is un-valid
                    if tag_name.startswith('sha256-') and \
                            (tag_name.endswith('.sbom') or tag_name.endswith('.sig') or tag_name.endswith('.att')):
                        continue
                    _tag_timestamp_dict[tag_name] = v['timeUploadedMs']
                    _tag_digest_dict[tag_name] = digest

            tag_list = utils.sort_dict(_tag_timestamp_dict)
            if len(tag_list):
                return True, tag_list, _tag_digest_dict

        return False, [], {}

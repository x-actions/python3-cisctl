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

""" quay Register API v2 """
import os

from cisctl import utils
from cisctl.api import RegisterBaseAPIV2
from cisctl.skopeo import Skopeo


class QuayRegisterV2(RegisterBaseAPIV2):

    def __init__(self, registry_url='https://quay.io', repo=None):
        super().__init__()
        self.base_url = f'{registry_url}/v2'
        self.skopeo = Skopeo()
        self.repo = repo

    def list_tags(self, name, n=10, next='') -> {}:  # noqa
        """ list special image tags
        Action: quay api is too hard to call, use Skopeo instead

        skopeo list-tags speaker

        GET https://quay.io/v2/metallb/speaker/tags/list
        GET https://quay.io/v2/metallb/speaker/tags/list?n=50&next_page=gAAAAABiKuXErTweWhOFkSPZXbeVDTAuP1_SyO2M7IDSuDnTVJlAGce0Gvv1gZFlaG1yKq4v_092ENhUu6LzEow-P2gAuNrjTn9lke0udu-Cd7nV8eBKYbA%3D

        :param name: speaker of quay.io/metallb/speaker
        :param n: page size
        :param next: next tag
        return:
        {
            "Repository": "quay.io/metallb/speaker",
            "Tags": [
                ...
                "main"
            ]
        }
        """
        return self.skopeo.list_tags(transport='docker', repo=f'quay.io/{self.repo}', name=name)

    def sort_tags(self, name) -> (bool, []):
        """ sort image tags dict to Z-A

        :param name: like controller
        :return: True, [(tag1, lastupdatets), ...]
        """
        tags = self.list_tags(name).get('Tags', [])
        _tag_dict = {}
        index = 0
        for tag in tags:
            _tag_dict[tag] = index
            index += 1
        tag_list = utils.sort_dict(_tag_dict)
        if len(tag_list):
            return True, tag_list

        return False, []

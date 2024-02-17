# Copyright 2023 xiexianbin.cn
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

""" kubernetes registry.k8s.io """

import json
from typing import Dict
from typing import List
from typing import Tuple

from cisctl.bash import Bash
from cisctl import utils
from cisctl.api import RegisterBaseAPIV2


class K8sRegister(RegisterBaseAPIV2):

    def __init__(self, registry_url: str='https://registry.k8s.io', project: str=None):
        super().__init__()
        self.base_url = registry_url.replace('https://', '').replace('/', '')
        self.bash = Bash()

    def list_tags(self, name, n=10, next='') -> {}:  # noqa
        """ list special image tags
        e.g.
          gcrane ls --json registry.k8s.io/addon-builder | jq .
        ref:
          - https://github.com/google/go-containerregistry/blob/main/cmd/gcrane/README.md

        :param name: addon-builder
        :return
            {
              "name": "k8s-artifacts-prod/images/addon-builder",
              "child": [],
              "tags": [
                "am-i-a-manifest-list",
                "latest",
                "latest_20180730",
                "test"
              ],
              "manifest": { ... }
            }
        """
        cmd = f'gcrane ls --json {self.base_url}/{name}'
        code, stdout, _ = self.bash.run(cmd, result=True)
        if code == 0:
            return True, json.loads(stdout)
        return False, {}

    def sort_tags(self, name) -> (bool, List[Tuple[str, int]], Dict):
        """ sort image tags dict to Z-A

        :param name: addon-builder or addon-manager/kube-addon-manager
        return:
        """
        result, resp = self.list_tags(name)
        if result:
            # error case:
            #   Run bash: gcrane ls --json registry.k8s.io/etcd-backup
            #   ret is 0
            #   stdout is {"child":null,"manifest":null,"name":"","tags":null}
            if resp.get('manifest') is None:
              return False, [], {}

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

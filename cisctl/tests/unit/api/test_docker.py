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

"""test python skopeo utils."""

import unittest

from cisctl.api.docker import DockerV2


class DockerV2TestCase(unittest.TestCase):

    def setUp(self):
        self.docker = DockerV2()

    def test_last_tag(self):
        name = 'gcmirrors/kube-apiserver'
        print(self.docker.last_tag(name))

        name = 'gcmirrors/no-exist'
        print(self.docker.last_tag(name))

    def test_last_tag(self):
        name = 'gcmirrors/kube-apiserver'
        print(self.docker.last_tag(name))

        name = 'gcmirrors/no-exist'
        print(self.docker.last_tag(name))

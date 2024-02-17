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

from cisctl.skopeo import Skopeo


class SkopeoTestCase(unittest.TestCase):

    def setUp(self):
        self.skopeo = Skopeo()

    def test_do_sync(self):
        src_repo = 'k8s.gcr.io'
        dest_repo = 'docker.io/gcmirrors'
        name = 'pause-amd64'
        src_transport = 'docker'
        dest_transport = 'docker'

        self.skopeo.do_sync(src_repo, dest_repo, name, src_transport, dest_transport)

    def test_sync_registry_k8s_io(self):
        src_repo = 'registry.k8s.io'
        dest_repo = 'docker.io/registryk8s'
        name = 'csi/csi-attacher'
        src_transport = 'registry.k8s.io'
        dest_transport = 'docker'

        self.skopeo.do_sync(src_repo, dest_repo, name, src_transport, dest_transport)

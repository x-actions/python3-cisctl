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

"""test utils."""

import unittest

from cisctl.shell import CIS


class CISTestCase(unittest.TestCase):

    def setUp(self):
        self.cis = CIS()

    def test_grc_sort_tags(self):
        src_repo, name = 'k8s.gcr.io', 'kube-apiserver'
        print(self.cis.grc_sort_tags(src_repo, name))

        src_repo, name = 'gcr.io/ml-pipeline', 'api-server'
        print(self.cis.grc_sort_tags(src_repo, name))

    def test_sync_image(self):
        image = 'k8s.gcr.io/kube-apiserver'
        print(self.cis.sync_image(image))

        image = 'gcr.io/ml-pipeline/api-server'
        print(self.cis.sync_image(image))

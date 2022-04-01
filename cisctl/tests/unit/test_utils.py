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

from cisctl import utils


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_date2timestamp(self):  # noqa
        date_time = '2020-06-28T11:46:53.539425Z'
        print(utils.date2timestamp(date_time))

    def test_generate_dest_name(self):  # noqa
        print(utils.generate_dest_name('gcr.io/knative-releases/knative.dev/eventing/cmd', 'appender'))
        print(utils.generate_dest_name('gcr.io/tekton-releases/github.com/tektoncd/triggers/cmd', 'webhook'))

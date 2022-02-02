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

"""python utils."""

import datetime
import os
import traceback

from cisctl.exception import CISException
from cisctl.logger import logger


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_repo_and_name(image) -> (str, str):
    """ parse image to (repo, name)

    :param image: gcr.io/google-containers/pause-amd64
    :return (repo, name): ('gcr.io/google-containers', 'pause-amd64')
    """
    t = image.split('/')
    return '/'.join(t[:-1]), t[-1]

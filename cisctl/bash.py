# Copyright 2020 xiexianbin.cn
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

"""python bash utils."""

import subprocess

from cisctl.logger import logger


class Bash(object):

    def __init__(self):
        self.logger = logger

    @staticmethod
    def run(command, result=False):
        args = ['bash', '-c', command]

        _sub_p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _stdout, _stderr = _sub_p.communicate()
        stdout, stderr = _stdout.decode(), _stderr.decode()
        code = _sub_p.poll()
        logger.info(f'Run bash: {command}, ret is {code}, stdout is {stdout}, stderr is: {stderr}')

        if result:
            return code, stdout, stderr

        return code

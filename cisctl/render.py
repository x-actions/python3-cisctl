# Copyright 2018 xiexianbin.cn
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

"""python git utils."""

import os

from jinja2 import Template

from cisctl import constants
from cisctl import utils


class Render(object):

    def __init__(self):
        pass

    def readme(self, images_list, src_org, src_repo):
        # for readme.md
        in_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template/README.md')
        out_path = os.path.join(constants.GIT_REPO, 'README.md')
        with open(in_path, 'r') as in_file, open(out_path, 'w') as out_file:
            tmpl = Template(in_file.read())
            out_file.write(tmpl.render({
                'images_list': images_list,
                'image_count': len(images_list),
                'date': utils.now(),
                'src_org': src_org,
                'src_repo': src_repo,
                'dest_repo': constants.DEST_REPO.split('/')[-1]
            }))

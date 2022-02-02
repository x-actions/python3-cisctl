#  Copyright 2022 xiexianbin.cn
#  All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#         http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""sync containers image from one register to others."""

import os

from multiprocessing import Pool

from cisctl import constants
from cisctl import http
from cisctl import utils
from cisctl.logger import logger
from cisctl.render import Render
from cisctl.skopeo import Skopeo


def _sync_image(image):
    logger.debug('Begin to sync image: [{}], sub pid is [{}]'.format(image, os.getpid()))
    src_repo, name = utils.parse_repo_and_name(image)
    _skopeo = Skopeo()
    src_image_tags = _skopeo.do_sync(
        src_repo,
        constants.DEST_REPO,
        name,
        constants.SRC_TRANSPORT,
        constants.DEST_TRANSPORT)
    return f'{"@@".join(src_image_tags)}@@@{name}'


def _do_sync():
    _target_images_list = http.get(constants.SRC_IMAGE_LIST_URL).split('\n')
    _result_images_list = []

    logger.info('init multiprocessing pool, main pid is [{}]'.format(os.getpid()))
    p = Pool(constants.THREAD_POOL_NUM)
    subprocess_result = []
    for image in _target_images_list:
        image = image.replace('\n', '')
        subprocess_result.append(p.apply_async(_sync_image, args=(image,)))

    for result in subprocess_result:
        r = result.get()
        r = r.split('@@@')
        src_image_tags = r[0].split('@@')

        _result_images_list.append({
            'name': r[1],
            'tags': src_image_tags,
            'tags_count': len(src_image_tags),
            'total_size': '-',
            'date': utils.now()})

    p.close()
    p.join()
    logger.info('All subprocess done.')

    src_org, src_repo, _ = _target_images_list[0].split('/')
    return _result_images_list, src_org, src_repo


def main():
    logger.info('--- Begin to sync images ---')
    _render = Render()
    # 1. do sync
    result_images_list, src_org, src_repo = _do_sync()

    # 2. render readme
    _render.readme(result_images_list, src_org, src_repo)

    logger.info('--- End to sync images ---')


if __name__ == "__main__":

    main()

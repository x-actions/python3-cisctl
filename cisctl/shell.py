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

from cisctl import constants, http
from cisctl import utils
from cisctl.api.docker import DockerV2
from cisctl.api.gcr import GoogleContainerRegisterV2
from cisctl.logger import logger
from cisctl.render import Render
from cisctl.skopeo import Skopeo


class CIS(object):

    def __init__(self):
        self._skopeo = Skopeo()
        self._docker = DockerV2()
        self._k8s_grc = GoogleContainerRegisterV2(registry_url='https://k8s.gcr.io')
        self._gcr = GoogleContainerRegisterV2()

    def grc_sort_tags(self, repo, name):
        _raw_name = name
        if repo.startswith('k8s.gcr.io'):
            _grc = self._k8s_grc
        else:
            _grc = self._gcr
            if '/' in repo:
                _raw_name = f'{repo.split("/")[-1]}/{name}'
        return _grc.sort_tags(_raw_name)

    def sync_image(self, image):
        """ sync image

        :param image: k8s.gcr.io/kube-apiserver or gcr.io/ml-pipeline/api-server
        """
        logger.debug('Begin to sync image: [{}], sub pid is [{}]'.format(image, os.getpid()))
        src_repo, name = utils.parse_repo_and_name(image)

        _, last_tag, last_timestamp = self._docker.last_tag(f'{constants.DEST_REPO}/{name}')

        _, gcr_sort_tags = self.grc_sort_tags(src_repo, name)
        gcr_sort_tags.reverse()
        flag = False

        for (_tag, _) in gcr_sort_tags:
            if flag is False and last_tag is None:
                flag = True

            if flag is False and _tag == last_tag:
                flag = True
                continue

            if flag is False:
                continue

            self._skopeo.copy(
                src_repo=src_repo,
                dest_repo=constants.DEST_REPO,
                name=name,
                tag=_tag,
                src_transport=constants.SRC_TRANSPORT,
                dest_transport=constants.DEST_TRANSPORT)

        return f'{"@@".join([_tag for _, _tag in gcr_sort_tags])}@@@{name}'

    def do_sync(self):
        headers = {
            'Content-Type': 'application/text'
        }
        result, resp = http.http_get(url=constants.SRC_IMAGE_LIST_URL, headers=headers)
        _target_images_list = resp.split('\n')
        _result_images_list = []

        logger.info('init multiprocessing pool, main pid is [{}]'.format(os.getpid()))
        p = Pool(constants.THREAD_POOL_NUM)
        subprocess_result = []
        for image in _target_images_list:
            image = image.replace('\n', '')
            if image.startswith('gcr.io/google-containers'):
                image = image.replace('gcr.io/google-containers', 'k8s.gcr.io')
            subprocess_result.append(p.apply_async(self.sync_image, args=(image,)))

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
    # 1. do sync
    _cis = CIS()
    result_images_list, src_org, src_repo = _cis.do_sync()

    # 2. render readme
    _render = Render()
    _render.readme(result_images_list, src_org, src_repo)

    logger.info('--- End to sync images ---')


if __name__ == "__main__":

    main()

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
from cisctl.api.quay import QuayRegisterV2
from cisctl.logger import logger
from cisctl.render import Render
from cisctl.skopeo import Skopeo


class CIS(object):

    def __init__(self):
        self._skopeo = Skopeo()
        self._docker = DockerV2()
        self._source_registry = None

    def init_source_registry_api(self, registry_url, repo=None):
        """ init source registry api

        :param registry_url: k8s.gcr.io or gcr.io or quay.io
        :param repo: is google cloud project
            - None : k8s.gcr.io/pause
            - ingress-nginx : k8s.gcr.io/ingress-nginx/controller
            - ml-pipeline : gcr.io/ml-pipeline/api-server
            - metallb : quay.io/metallb/controller
        :return: None
        """
        if self._source_registry is None:
            if registry_url.startswith('k8s.gcr.io'):
                self._source_registry = GoogleContainerRegisterV2(registry_url='https://k8s.gcr.io', project=repo)
            elif registry_url.startswith('gcr.io'):
                self._source_registry = GoogleContainerRegisterV2(registry_url='https://gcr.io', project=repo)
            elif registry_url.startswith('quay.io'):
                self._source_registry = QuayRegisterV2(registry_url='https://gcr.io', repo=repo)

    def sync_image(self, image):
        """ sync image

        :param image: k8s.gcr.io/pause or gcr.io/ml-pipeline/api-server or quay.io/metallb/controller
        """
        logger.debug(f'Begin to sync image: [{image}], sub pid is [{os.getpid()}]')
        src_repo, name = utils.parse_repo_and_name(image)
        if '/' in src_repo:
            registry_url, repo = src_repo.split('/')
            self.init_source_registry_api(registry_url, repo)
        else:
            self.init_source_registry_api(src_repo)

        _, last_tag, last_timestamp = self._docker.last_tag(f'{constants.DEST_REPO}/{name}')
        _, src_sort_tags = self._source_registry.sort_tags(name)
        src_sort_tags.reverse()
        flag = False

        for (_tag, _) in src_sort_tags:
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

        return f'{"@@".join([_tag for (_tag, _) in src_sort_tags])}@@@{name}'

    def do_sync(self):
        headers = {
            'Content-Type': 'application/text'
        }
        result, resp = http.http_get(url=constants.SRC_IMAGE_LIST_URL, headers=headers)
        _target_images_list = resp.split('\n')
        _result_images_list = []

        logger.info(f'init multiprocessing pool, main pid is [{os.getpid()}]')
        p = Pool(constants.THREAD_POOL_NUM)
        subprocess_result = []
        for image in _target_images_list:
            image = image.replace('\n', '')
            # skip empty and '#" image
            if image == '' or '#' in image:
                continue
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

        _target_info = _target_images_list[0].split('/')
        src_org, src_repo = _target_info[0], _target_info[1]
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

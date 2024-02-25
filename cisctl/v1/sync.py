# Copyright 2024 xiexianbin.cn
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

"""sync containers image from one register to others."""

import os
import time

from multiprocessing import Pool

from cisctl import client, config
from cisctl import utils
from cisctl.api.docker import DockerV2
from cisctl.api.gcr import GoogleContainerRegisterV2
from cisctl.api.k8s import K8sRegister
from cisctl.api.quay import QuayRegisterV2
from cisctl.logger import logger
from cisctl.skopeo import Skopeo


class CIS(object):
    """sync Container Images."""
    def __init__(self, src_transport: str, dest_transport: str, after_timeuploadedms: int = 0):
        self._skopeo = Skopeo()
        self._docker = DockerV2()
        self._source_registry = None

        self.src_transport = src_transport
        self.dest_transport = dest_transport
        self.after_timeuploadedms = after_timeuploadedms

    def init_source_registry_api(self, registry_url, repo=None):
        """ init source registry api

        :param registry_url: k8s.gcr.io or gcr.io or quay.io
        :param repo: is google cloud project
            - None : k8s.gcr.io/pause
            - ingress-nginx : k8s.gcr.io/ingress-nginx/controller
            - ml-pipeline : gcr.io/ml-pipeline/api-server
            - metallb : quay.io/metallb/controller
            - knative-releases/knative.dev/eventing/cmd : gcr.io/knative-releases/knative.dev/eventing/cmd/webhook
        :return: None
        """
        if self._source_registry is None:
            if registry_url.startswith('gcr.io'):
                self._source_registry = GoogleContainerRegisterV2(registry_url='https://gcr.io', project=repo)
            elif registry_url.startswith('k8s.gcr.io'):
                self._source_registry = GoogleContainerRegisterV2(registry_url='https://k8s.gcr.io', project=repo)
            elif registry_url.startswith('quay.io'):
                self._source_registry = QuayRegisterV2(registry_url='https://quay.io', repo=repo)
            elif registry_url.startswith('registry.k8s.io'):
                self._source_registry = K8sRegister(registry_url='https://registry.k8s.io', project=repo)

    def sync_image(self, image: str, dest_repo: str):
        """ sync image

        :param image: one of
        - k8s.gcr.io/pause
        - gcr.io/ml-pipeline/api-server
        - quay.io/metallb/controller
        - gcr.io/knative-releases/knative.dev/eventing/cmd/webhook
        - registry.k8s.io/addon-builder
        - registry.k8s.io/csi/csi-attacher
        :param dest_repo(str): e.g. docker.io/gcmirrors
        """
        logger.debug(f'Begin to sync image: [{image}], sub pid is [{os.getpid()}]')
        src_repo, name = utils.parse_repo_and_name(image)
        dest_name = utils.generate_dest_name(src_repo, dest_repo, name)
        if '/' in src_repo:
            registry_url, repo = utils.parse_registry_url_and_project(src_repo)
            self.init_source_registry_api(registry_url, repo)
        else:
            self.init_source_registry_api(src_repo)

        _, src_sort_tags, src_tag_digest_dict = self._source_registry.sort_tags(name)
        src_sort_tags.reverse()

        target_image_name = f'{dest_repo}/{dest_name}'
        result, synced_tags_with_timestamp, synced_tag_digest_dict = \
            self._docker.sort_tags(target_image_name)
        last_tag, last_timestamp = self._docker.last_tag(target_image_name, synced_tags_with_timestamp)

        # call docker api occur exception, skip sync
        if result is False and last_tag is None and last_timestamp is None:
            logger.warning(f'sync image {image}, docker api limit, exist.')
            # the result is need to sync
            return f'{"@@".join([_tag for (_tag, _) in src_sort_tags])}@@@{dest_name}'

        do_sync_flag = False
        next_do_sync_flag = False
        if last_tag is None:  # never synced
            do_sync_flag = True
        synced_flag = False
        synced_tags = {k for k, _ in synced_tags_with_timestamp}
        for (src_tag, src_uploaded_timestamp) in src_sort_tags:
            src_tag_digest = src_tag_digest_dict.get(src_tag)
            synced_tag_digest = synced_tag_digest_dict.get(src_tag)

            if do_sync_flag is False and int(src_uploaded_timestamp) > self.after_timeuploadedms:
                # check already synced flag
                if synced_flag is False and src_tag != 'latest' and src_tag in synced_tags:
                    synced_flag = True

                # if oldest tag is sync and new tag not in synced_tags, do sync
                # fix some tag not sync bug
                if synced_flag is True and src_tag not in synced_tags:
                    do_sync_flag = True

                # if src_uploaded_timestamp > last_timestamp: src is update, do sync
                if last_timestamp is not None and int(src_uploaded_timestamp) > int(last_timestamp):
                    do_sync_flag = True

                # already synced but image digest is not match, do sync again
                # TODO: xiexianbin, not fix https://www.xiexianbin.cn/container/tools/skopeo/#fq
                # if synced_flag is True and src_tag_digest is not None \
                #         and synced_tag_digest is not None \
                #         and src_tag_digest != synced_tag_digest:
                #     do_sync_flag = True

                # update do_sync_flag to True
                if src_tag == 'latest' or next_do_sync_flag is True:
                    do_sync_flag = True

                # find last synced image tag, update next_do_sync_flag to True
                if src_tag == last_tag:
                    next_do_sync_flag = True

            # skip condition: already synced tags
            if do_sync_flag is False:
                continue
            if do_sync_flag is True and src_tag_digest is not None \
                    and synced_tag_digest is not None \
                    and src_tag_digest == synced_tag_digest:
                continue

            self._skopeo.copy(
                src_repo=src_repo,
                dest_repo=dest_repo,
                name=name,
                tag=src_tag,
                dest_name=dest_name,
                src_transport=self.src_transport,
                dest_transport=self.dest_transport)

        return f'{"@@".join([_tag for (_tag, _) in src_sort_tags])}@@@{dest_name}'

    def do_sync(self, src_image_list_url: str, thread_pool_size: int,
                dest_repo: str, job_batch_size: int, debug: bool):
        headers = {
            'Content-Type': 'application/text'
        }
        result, resp = client.http_get(url=src_image_list_url, headers=headers)
        _target_images_list = resp.split('\n')
        target_images_list = []
        for image in _target_images_list:
            image = image.replace('\n', '')
            # skip empty and '#" image
            if image == '' or image.startswith("#"):
                continue
            target_images_list.append(image)
        result_images_list = []

        logger.info(f'init multiprocessing pool, main pid is [{os.getpid()}]')
        p = Pool(thread_pool_size)
        subprocess_result = []

        # fix Docker API Rate Limiting
        if len(target_images_list) > 180 and dest_repo.startswith("docker.io"):
            interval_hour = 24 / job_batch_size
            batch_num = int(time.localtime().tm_hour / interval_hour)
            images_count_per_job = int(len(target_images_list) / job_batch_size) + 1

            start_index = batch_num * images_count_per_job
            end_index = (batch_num + 1) * images_count_per_job - 1
            target_images_list = target_images_list[start_index:end_index+1]
            logger.info(
                f'BATCH Jobs matched, start_index is {start_index}, end_index is {end_index}, '
                f'JOB_BATCH_COUNT is {job_batch_size}, batch_num is {batch_num}, '
                f'images_count_per_job is {images_count_per_job}, begin to sync image size '
                f'is {len(target_images_list)}')

        for image in target_images_list:
            if image.startswith('gcr.io/google-containers'):
                image = image.replace('gcr.io/google-containers', 'k8s.gcr.io')
            subprocess_result.append(p.apply_async(self.sync_image, args=(image, dest_repo,)))

        for result in subprocess_result:
            r = result.get()
            r = r.split('@@@')
            if len(r) != 2:
                continue

            src_image_tags = r[0].split('@@')

            result_images_list.append({
                'name': r[1],
                'tags': src_image_tags,
                'tags_count': len(src_image_tags),
                'total_size': '-',
                'date': utils.now()})

        p.close()
        p.join()
        logger.info('All subprocess done.')

        _target_info = target_images_list[0].split('/')
        src_org, src_repo = _target_info[0], _target_info[1]
        return result_images_list, src_org, src_repo

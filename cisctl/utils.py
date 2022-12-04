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
import time
from datetime import datetime

import collections
try:
    from collections import abc
    collections.Counter = abc.Counter  # noqa
except Exception as _:  # noqa
    pass


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timestamp() -> int:
    return int(time.time() * 1000)


def parse_repo_and_name(image) -> (str, str):
    """ parse image to (repo, name)

    :param image: one of
        - k8s.gcr.io/pause
        - gcr.io/ml-pipeline/api-server
        - quay.io/metallb/controller
        - gcr.io/knative-releases/knative.dev/eventing/cmd/webhook
    :return (repo, name): one of
        - ('k8s.gcr.io', 'pause-amd64')
        - ('gcr.io/ml-pipeline', 'api-server')
        - ('quay.io/metallb', 'controller')
        - ('gcr.io/knative-releases/knative.dev/eventing/cmd', 'webhook')
    """
    t = image.split('/')
    return '/'.join(t[:-1]), t[-1]


def parse_registry_url_and_project(src_repo) -> (str, str):
    """ parse image to (registry_url, repo)

    :param src_repo: one of
        - k8s.gcr.io
        - gcr.io/ml-pipeline
        - quay.io/metallb
        - gcr.io/knative-releases/knative.dev/eventing/cmd
    :return (repo, name): one of
        - ('k8s.gcr.io', None)
        - ('gcr.io', 'ml-pipeline')
        - ('quay.io', 'metallb')
        - ('gcr.io', 'knative-releases/knative.dev/eventing/cmd')
    """
    t = src_repo.split('/')
    if len(t) == 1:
        return t[0], None
    return t[0], '/'.join(t[1:])


def sort_dict(d):
    """ sort dict to Z-A

    :param d: {'hello': 1, 'python': 5, 'world': 3}
    :return [('python', 5), ('world', 3), ('hello', 1)]
    """
    return collections.Counter(d).most_common()


def date2timestamp(date_time) -> int:
    """ convert date to millisecond timestamp

    :param date_time: 2020-06-28T11:46:53.539425Z / 2022-10-27T10:54:56Z
    :return timestamp: 1593316013539
    """
    try:
        dt_utc = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        return int(dt_utc.timestamp() * 1000)
    except ValueError:
        dt_utc = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%SZ')
        return int(dt_utc.timestamp() * 1000)


def generate_dest_name(src_repo, name):
    """ generate dest repo image name

    :param src_repo: one of
        - k8s.gcr.io
        - gcr.io/ml-pipeline
        - quay.io/metallb
        - gcr.io/knative-releases/knative.dev/eventing/cmd
        - gcr.io/knative-releases/knative.dev/eventing/cmd/in_memory # channel_controller -> eventing-in_memory-channel_controller
    :param name: image name
    :return dest_image_name
    """
    if '/cmd' in src_repo:
        t = src_repo.split('/')
        if t[-1] == 'cmd':
            return f'{t[-2]}-{name}'
        if t[-2] == 'cmd':
            return f'{t[-3]}-{t[-1]}-{name}'
        return f'{t}-{name}'

    return name

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

from datetime import datetime

from collections import Counter


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_repo_and_name(image) -> (str, str):
    """ parse image to (repo, name)

    :param image: k8s.gcr.io/kube-apiserver or gcr.io/ml-pipeline/api-server
    :return (repo, name): ('k8s.gcr.io', 'pause-amd64') or ('gcr.io/ml-pipeline', 'api-server')
    """
    t = image.split('/')
    return '/'.join(t[:-1]), t[-1]


def sort_dict(d):
    """ sort dict to Z-A

    :param d: {'hello': 1, 'python': 5, 'world': 3}
    :return [('python', 5), ('world', 3), ('hello', 1)]
    """
    return Counter(d).most_common()


def date2timestamp(date_time) -> int:
    """ convert date to millisecond timestamp

    :param date_time: 2020-06-28T11:46:53.539425Z
    :return timestamp: 1593316013539
    """
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt_utc = datetime.strptime(date_time, TIME_FORMAT)
    return int(dt_utc.timestamp() * 1000)

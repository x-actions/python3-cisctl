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

import os


CURRENT_PATH = os.getcwd()

# Github info display sync result
GIT_TOKEN = os.environ.get('GIT_TOKEN', 'github_token')
GIT_ORG = os.environ.get('GIT_ORG', 'x-mirrors')
GIT_REPO = os.environ.get('GIT_REPO', 'gcmirrors')

# skopeo args
"""
list like:
k8s.gcr.io/pause-amd64
gcr.io/ml-pipeline/api-server
"""
SRC_IMAGE_LIST_URL = os.environ.get(
    'SRC_IMAGE_LIST_URL',
    'https://raw.githubusercontent.com/x-mirrors/gcr.io/main/k8s.txt')
DEST_REPO = os.environ.get('DEST_REPO', f'docker.io/{GIT_REPO}')
SRC_TRANSPORT = os.environ.get('SRC_TRANSPORT', 'docker')
DEST_TRANSPORT = os.environ.get('DEST_TRANSPORT', 'docker')

# thread pool
THREAD_POOL_NUM = int(os.environ.get('THREAD_POOL_NUM', 2))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

# Only work when source is docker, because https://docs.docker.com/docker-hub/api/latest/#tag/rate-limiting
JOB_BATCH_COUNT = int(os.environ.get('JOB_BATCH_COUNT', 3))

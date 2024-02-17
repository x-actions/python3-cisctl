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

import os

from cisctl import config
from cisctl import utils
from cisctl.v1 import render
from cisctl.v1 import sync


# @utils.arg('foo', metavar='<foo>', help='foo action.')
# # @utils.arg(
# #     'foos', metavar='<foos>', nargs='+', # 支持传多个
# #     help='foo(s) actions.')
# @utils.arg(
#     '--int', dest='i1', metavar='<integer>', type=int, default=0,
#     help='some int value.')
# @utils.arg(
#     '--str', metavar='<str>', help='str action.',
#     default="str")
# @utils.arg(
#     '--bool',
#     dest='b1',
#     action="store_true",
#     default=False,
#     help='some bool value.')
# def do_foo(args):
#     """foo action for test."""
#     print(f"run foo ok, foo=[{args.foo}] --int={args.i1} --str={args.str} --bool={args.b1} --debug={args.debug}")

@utils.arg(
    '--src-transport', metavar='<str>',
    help='src transport',
    default="")
@utils.arg(
    '--dest-transport', metavar='<str>',
    help='dest transport',
    default="")
@utils.arg(
    '--git-repo', metavar='<str>', help='git repo',
    default="gcmirrors")
@utils.arg(
    '--src-image-list-url', metavar='<url>',
    help='src image list url',
    default="https://github.com/x-mirrors/gcr.io/raw/main/registry.k8s.io/all-repos.txt")
@utils.arg(
    '--thread-pool-size', dest='thread_pool_size', metavar='<integer>', type=int, default=2,
    help='thread pool size.')
@utils.arg(
    '--dest-repo', metavar='<str>',
    help='dest repo',
    default="")
@utils.arg(
    '--job-batch-size', dest='job_batch_size', metavar='<integer>', type=int, default=3,
    help='job batch size.')
@utils.arg(
    '--src-image-list-url', metavar='<url>',
    help='src image list url',
    default="https://github.com/x-mirrors/gcr.io/raw/main/registry.k8s.io/all-repos.txt")
@utils.arg(
    '--after-timeuploadedms', dest='after_timeuploadedms', metavar='<integer>', type=int, default=0,
    help='job batch size.')
def do_sync(args):
    """sync Container Images."""
    # 1. do sync
    _cis = sync.CIS(
        src_transport=args.src_transport if args.src_transport else os.environ.get('SRC_TRANSPORT', 'docker'),
        dest_transport=args.dest_transport if args.dest_transport else os.environ.get('DEST_TRANSPORT', 'docker'),
        after_timeuploadedms=args.after_timeuploadedms if args.after_timeuploadedms else int(os.environ.get('AFTER_TIMEUPLOADEDMS', 0)))

    _git_repo=args.git_repo if args.git_repo else os.environ.get('GIT_REPO', 'gcmirrors')
    _dest_repo = args.dest_repo if args.dest_repo else os.environ.get('DEST_REPO', f'docker.io/{_git_repo}')

    result_images_list, src_org, src_repo = _cis.do_sync(
        src_image_list_url=args.src_image_list_url if args.src_image_list_url else os.environ.get(
            'SRC_IMAGE_LIST_URL', 'https://github.com/x-mirrors/gcr.io/raw/main/registry.k8s.io/all-repos.txt'),
        thread_pool_size=args.thread_pool_size if args.thread_pool_size else int(os.environ.get('THREAD_POOL_NUM', 2)),
        dest_repo=_dest_repo,
        job_batch_size=args.job_batch_size if args.job_batch_size else int(os.environ.get('JOB_BATCH_COUNT', 3)),  # Only work when source is docker, because https://docs.docker.com/docker-hub/api/latest/#tag/rate-limiting
        debug=True if args.debug == 'DEBUG' else os.environ.get('LOG_LEVEL', False),
    )

    # 2. render readme
    _render = render.Render()
    _render.readme(result_images_list, src_org, src_repo, dest_repo=_dest_repo, git_repo=_git_repo)

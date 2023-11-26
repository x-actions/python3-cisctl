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


def do_sync(args):
    """sync Container Images."""
    # 1. do sync
    _cis = sync.CIS()
    result_images_list, src_org, src_repo = _cis.do_sync()

    # 2. render readme
    _render = render.Render()
    _render.readme(result_images_list, src_org, src_repo)

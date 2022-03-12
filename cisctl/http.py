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

"""python http utils."""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3

from cisctl.logger import logger

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
timeout = 200


def _gen_header(header):
    if header is None:
        return {
            'Content-Type': 'application/json'
        }
    else:
        return header


def _http_request(method, url, headers=None, data=None):
    try:
        if method == 'GET':
            resp = requests.get(url=url, headers=headers, params=data, verify=False)
        elif method == 'HEAD':
            resp = requests.head(url=url, headers=headers, verify=False)
        elif method == 'POST':
            resp = requests.post(url=url, headers=headers, json=data, verify=False)
        elif method == 'DELETE':
            resp = requests.delete(url=url, headers=headers, json=data, verify=False)
        elif method == 'PUT':
            resp = requests.put(url=url, headers=headers, json=data, verify=False)
        else:
            return False, None
    except requests.exceptions.RequestException:
        logger.exception(f'http request error! type: {method}, url: {url}, data: {str(data)}')
        return False, None
    else:
        if resp.status_code != 200:
            content = resp.content[:100] if resp.content else ''
            logger.error(f'http request error! type: {method}, url: {url}, data: {str(data)}, '
                         f'response_status_code: {resp.status_code}, response_content: {content}')
            return False, None

        logger.debug(f'http request success! type: {method}, url: {url}, data: {str(data)}, '
                     f'response_status_code: {resp.status_code}, response_content: {resp.text}')

        if headers.get('Content-Type', None) == 'application/json':
            return True, resp.json()
        else:
            return True, resp.text


def http_get(url, data=None, headers=None):
    headers = _gen_header(headers)
    return _http_request(method='GET', url=url, headers=headers, data=data)


def http_post(url, data, headers=None):
    headers = _gen_header(headers)
    return _http_request(method='POST', url=url, headers=headers, data=data)


def http_delete(url, headers=None):
    headers = _gen_header(headers)
    return _http_request(method='DELETE', url=url, headers=headers)

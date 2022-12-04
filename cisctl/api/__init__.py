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
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple


class RegisterBaseAPIV2(object):

    def __init__(self):
        pass

    def list_tags(self, name, **kwargs) -> Any:
        raise NotImplemented

    def sort_tags(self, name) -> (bool, List[Tuple[str, int]], Dict):
        """ return sorted tags by timestamp desc

        :param name: image name
        :return: (bool, List[Tuple[str, int]], Dict)
        Dict is image's tag and sha256 map
        e.g. (True, [(tag1, last_update_timestamp), ...], {tag1: sha2561, ...})
        """
        raise NotImplemented

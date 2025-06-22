# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from setuptools import setup, find_packages
from datetime import datetime

PROJECT_NAME = "ntdocs"

# Generate a version like 1.0.0.2506041530 (DDMMYYHHMM)
date_version = datetime.now().strftime("%y%m%d%H%M")
VERSION = f"1.0.0.{date_version}"

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description='',
    long_description='',
    license='',

    packages=find_packages(),
    package_data={
        PROJECT_NAME: [
            # 'data/**/*',
            # 'data/**/**/*',
            'base/**/*',
            'base/**/**/*',
        ]
    },
    zip_safe=False,
)


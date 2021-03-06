#!/usr/bin/python
#
# Copyright 2014 Google Inc.
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
#
################################################################################
#
# Config processing and expansion.

import json
import sys

# Local imports
import gce


def ImportModule(module):
  config = __import__(module, globals={}, locals={}, fromlist=['*'])
  return config.resources


def CompileAndEvalFile(path):
  module_globals = {}
  module_locals = {}

  # We shouldn't use "from gce import *" here due to:
  #   SyntaxWarning: import * only allowed at module level
  # so we emulate it instead by adding all top-level symbols to globals.
  for key, val in gce.__dict__.iteritems():
    module_globals[key] = val

  execfile(path, module_globals, module_locals)
  return module_locals['resources']


class ConfigExpander(object):
  def __init__(self, **kwargs):
    self.__kwargs = {}
    for key, value in kwargs.iteritems():
      self.__kwargs[key] = value

    project = None
    if 'project' in self.__kwargs:
      project = self.__kwargs['project']
    zone = None
    if 'zone' in self.__kwargs:
      zone = self.__kwargs['zone']

    gce.GCE.setCurrent(project=project, zone=zone)

  def ExpandFile(self, file_name):
    return CompileAndEvalFile(file_name)


def main(argv):
  if len(argv) < 2:
    sys.stderr.write('''\
Syntax: %s [python module or file]

Note: using .py suffix simplifies your code and allows skipping the boilerplate
header, e.g., "from resources import *" but uses compile() + eval().

Skipping the .py suffix causes the file to be treated as a Python modile which
requires adding the import line manually and will use __import__() as the
mechanism.
''' % argv[0])
    sys.exit(1)

  path = argv[1]
  if path.endswith('.py'):
    resources = CompileAndEvalFile(path)
  else:
    resources = ImportModule(path)
  print('%s' % json.dumps(resources, indent=2, separators=(',', ': '), sort_keys=True))


if __name__ == '__main__':
  main(sys.argv)

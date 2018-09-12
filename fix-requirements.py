#!/usr/bin/env python

import re
import argparse
import sys

from os import unlink
from shutil import copyfile


def get_vers(lines=[]):
  version_map = {}

  #lines look like this: alabaster (0.7.6)
  r = re.compile('^(.+)\ \((.+)\)')

  for l in lines:
    m = r.match(l)
    version_map[m.group(1)] = m.group(2)

  return version_map


def fix_reqs(requirements, version_map, die_on_errors=False):
  to_return = []
  split_chars = re.compile('\<|\!|\>|\=')
  valid_version = re.compile('^(\d+)+(\.\d+)?(\.\d+)?$')
  for r in requirements:
    result = split_chars.split(r)
    if result[0] in version_map:
      #This means that we need to replace it with what is in version_map
      to_return.append('%s==%s' % (result[0], version_map[result[0]]))
      if not valid_version.search(version_map[result[0]]):
        sys.stderr.write("ERROR: Authoritative versions has %s for package" \
                         " %s. This will most likely break things!\n" %
                         (version_map[result[0]], result[0]))
      if die_on_errors:
        sys.exit(1)

    else:
      sys.stderr.write("ERROR: '%s' found in requirements, but not in" \
                       " authoritative map!\n" % result[0].rstrip())
      to_return.append(r.rstrip())
      if die_on_errors:
        sys.exit(1)


  return to_return


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
                      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--requirements_file', default='requirements.txt',
           help='Path to a pip style requirements.txt file.')
  parser.add_argument('--map_file', default='libs.vers',
           help='The output of `pip list` from some authoritative source.')
  parser.add_argument('--inplace', default=False, action='store_true',
           help='Used to modify REQUIREMENTS_FILE in-place. Creates a backup.')
  parser.add_argument('--no_ignore_errors', default=False, action='store_true',
           help='Stop execution instead of just printing errors.')
  args = parser.parse_args()
  map_file = open(args.map_file, 'r')
  req_file = open(args.requirements_file, 'r')
  vs = get_vers(map_file.readlines())
  new_reqs = fix_reqs(req_file.readlines(), vs, args.no_ignore_errors)
  if args.inplace is True:
    req_file.close()
    copyfile(args.requirements_file, '%s~' % args.requirements_file)
    unlink(args.requirements_file)
    f = open(args.requirements_file,'w')
    for l in new_reqs:
      f.write('%s\n' % l)
    f.close()
  else:
    for i in new_reqs:
      print(i)

# command line utility to manage tiled windows
from util import *
from manager import *
import sys
from pathlib import Path

# print help thing
def print_usage():
  print('Usage: python3 tile.py [reset|list]')

if __name__ == '__main__':
  # to store the window state
  stash = str(Path.home()) + '/.tiling_configuration'

  if len(sys.argv) == 1:
    print_usage()
    exit()
  option = sys.argv[1]

  # force tile all windows & initialize stash
  if option == 'reset':
    manager = Manager.from_reality()
    manager.render()
    open(stash, 'w').write(repr(manager))
    exit()

  if not Path(stash).is_file():
    print('Error: `{}` does not exist yet\nRun `python3 tile.py reset` first'.format(stash))
    exit()

  with open(stash, 'r') as f:
    manager = Manager.from_str(f.read())

  # list the workspace trees
  if option == 'list':
    print(manager)

  else:
    print('Unrecognized option `{}`'.format(option))
    print_usage()

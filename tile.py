# command line utility to manage tiled windows
from util import *
from tree import *
import sys
from pathlib import Path

# force all workspaces to tile properly
def reset() -> Dict[int, Tree]:
  windows = extract_windows()
  trees = {}
  for workspace, ids in windows.items():
    trees[workspace] = Tree.from_list(ids)
    trees[workspace].render()
  return trees

# string representation of the workspace trees
def stringify(trees : Dict[int, Tree]) -> str:
  return '\n'.join('{} {}'.format(workspace, tree.rpn()) for workspace, tree in trees.items())

# extract workspace trees from string representation
def parse(s:str) -> Dict[int, Tree]:
  lines = (a.split() for a in s.split('\n'))
  workspaces:Dict[int, Tree] = {}
  for l in lines:
    workspace = int(l[0])
    rpn = ' '.join(l[1:])
    workspaces[workspace] = Tree.from_rpn(rpn)
  return workspaces

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
    open(stash, 'w').write(stringify(reset()))
    exit()

  # check that the stash exists
  if not Path(stash).is_file():
    print('Error: `{}` does not exist yet\nRun `python3 tile.py reset` first'.format(stash))
    exit()

  # read in the trees from the stash
  with open(stash, 'r') as f:
    trees = parse(f.read())

  # list the workspace trees
  if option == 'list':
    for workspace, tree in trees.items():
      print('{}: {}'.format(workspace, tree))

  else:
    print('Unrecognized option `{}`'.format(option))
    print_usage()

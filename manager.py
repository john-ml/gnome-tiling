from util import *
from tree import *
from typing import *

# a set of workspaces. essentially Dict[int, Tree]
class Manager:
  def __init__(self, workspaces : Dict[int, Tree]):
    self.workspaces = workspaces

  def __str__(self) -> str:
    return '\n'.join(
      '{}: {}'.format(workspace, tree) for workspace, tree in self.workspaces.items())

  def __repr__(self) -> str:
    return '\n'.join(
      '{} {}'.format(workspace, tree.rpn()) for workspace, tree in self.workspaces.items())

  # apply the stored window properties to the actual windows
  def render(self) -> None:
    for _, workspace in self.workspaces.items():
      workspace.render()

  # construct from the actual current window configuration
  @staticmethod
  def from_reality():
    from os import popen

    # extract window information
    # output is 1 line per window, containing:
    #   id workspace left top width height username title
    # just need id & workspace
    s = 'wmctrl -l -G'
    if DEBUG:
      print(s)
    entries = (l.split() for l in popen(s).read().split('\n'))

    # need to filter out:
    #   the empty list from the newline at the end of the input
    #   the Desktop "window" that shows up and takes up all of workspace 0
    entries = filter(lambda a: len(a) >= 8 and not ' '.join(a[7:]) == 'Desktop', entries)

    # construct workspace dict
    lists:Dict[int, List[int]] = {}
    for entry in entries:
      id, workspace = int(entry[0], 16), int(entry[1], 16)
      if workspace not in lists:
        lists[workspace] = [id]
      else:
        lists[workspace].append(id)

    # construct tiled trees for each workspace
    workspaces:Dict[int, Tree] = {}
    for workspace, ids in lists.items():
      workspaces[workspace] = Tree.from_list(ids)

    return Manager(workspaces)

  # construct from string representation returned by __repr__
  @staticmethod
  def from_str(s:str):
    lines = (a.split() for a in s.split('\n'))

    workspaces:Dict[int, Tree] = {}
    for l in lines:
      workspace = int(l[0])
      rpn = ' '.join(l[1:])
      workspaces[workspace] = Tree.from_rpn(rpn)

    return Manager(workspaces)

from util import *
from tree import *
from typing import *

# a set of workspaces. essentially Dict[int, Tree]
class Manager:
  def __init__(self, workspaces : Dict[int, Tree]) -> None:
    self.workspaces = workspaces

  def __str__(self) -> str:
    return '\n'.join(
      '{}: {}'.format(workspace, tree) for workspace, tree in self.workspaces.items())

  def __repr__(self) -> str:
    return '\n'.join(
      '{} {}'.format(workspace, tree.rpn()) for workspace, tree in self.workspaces.items())

  # insert a new window
  def insert(self, workspace:int, i:int):
    self.workspaces[workspace] = self.workspaces[workspace].insert(i)
    return self

  # get workspace on which some window exists
  def workspace_of(self, i:int) -> Union[int, None]:
    for w, tree in self.workspaces.items():
      if i in tree.ids():
        return w
    return None

  # focus a window in some direction away from the current active window
  def focus(self, direction:str):
    a = active_window()
    if a is None:
      return self
    a = fst(a)

    of = {
      'left': lambda w: w.left_of(a),
      'right': lambda w: w.right_of(a),
      'above': lambda w: w.above(a),
      'below': lambda w: w.below(a)}

    if direction not in of:
      raise ValueError('`{}` is not a valid direction'.format(direction))

    w = self.workspace_of(a)
    if w is None:
      return self
    w = self.workspaces[w]

    nearest = w.nearest(a, of[direction](w), direction)
    #print('direction', direction, w.right_of(a), hex(a), 'nearest', nearest)
    if nearest is None:
      return self

    focus_window(fst(nearest))
    return self

  # apply the stored window geometries to the actual windows
  def render(self):
    for _, workspace in self.workspaces.items():
      workspace.render()
    return self

  # construct from the actual current window configuration
  @staticmethod
  def from_reality():
    # extract window information
    # output is 1 line per window, containing:
    #   id workspace left top width height username title
    # just need id & workspace
    entries = (l.split() for l in run('wmctrl -l -G').split('\n'))

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

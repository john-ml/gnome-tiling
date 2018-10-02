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

  # close the currently active window
  def close(self):
    a = active_window()
    if a is None:
      return self
    i, w = a

    if type(self.workspaces[w]) is Leaf: # close the only window in the entire workspace
      del self.workspaces[w]
    else:
      self.workspaces[w] = self.workspaces[w].delete(i)
    run('wmctrl -i -c {}'.format(hex(i)))

    self.render()
    return self

  # transpose the active window
  def transpose(self):
    a = active_window()
    if a is None:
      return self
    i, w = a

    self.workspaces[w].transpose(i)
    self.render()
    return self

  # move active window to another workspace
  def move(self, target:int):
    a = active_window()
    if a is None:
      return self
    i, w = a

    if w == target:
      return

    # compute nearest window to focus after currect active window gets moved away
    a1 = self.workspaces[w].nearest(i, self.workspaces[w].windows(), 'left')
    if a1 is not None:
      run('wmctrl -i -a {}'.format(hex(fst(a1))))

    if type(self.workspaces[w]) is Leaf:
      del self.workspaces[w]
    else:
      self.workspaces[w] = self.workspaces[w].delete(i)

    if target not in self.workspaces:
      self.workspaces[target] = Leaf(i)
    else:
      self.workspaces[target] = self.workspaces[target].insert(i)

    run('wmctrl -i -r {} -t {}'.format(hex(i), target))

    self.render()
    return self

  # apply some function(a:int, w:Tree, nearest:Window)
  #   a is the id of the active window
  #   w is the workspace
  #   nearest is the nearest window to the active window in the given direction
  def act_directionally(self, direction:str, f):
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

    #print('before', w)
    f(a, w, nearest)
    #print('after', w)
    return self

  # focus a window in some direction away from the current active window
  def focus(self, direction:str):
    return self.act_directionally(
      direction,
      lambda _, __, nearest: focus_window(fst(nearest)))

  # swap with a window in some direction away from the current active window
  def swap(self, direction:str):
    self.act_directionally(
      direction,
      lambda a, workspace, nearest: workspace.swap(a, fst(nearest)))

    self.render()
    return self

  # apply the stored window geometries to the actual windows
  def render(self):
    for _, workspace in self.workspaces.items():
      workspace.render()
    return self

  # discover differences between current state & stored stash, and update accordingly
  def refresh(self):
    for w, ids in extract_windows().items():
      # brand new workspace
      if w not in self.workspaces:
        self.workspaces[w] = Tree.from_list(list(ids))
        continue

      old_ids = self.workspaces[w].ids()

      # remove nonexistent windows
      for i in old_ids - ids:
        self.workspaces[w] = self.workspaces[w].delete(i)

      # add new windows
      for i in ids - old_ids:
        self.workspaces[w] = self.workspaces[w].insert(i)

    self.render()
    return self

  # construct from the actual current window configuration
  @staticmethod
  def from_reality():
    # construct tiled trees for each workspace
    workspaces:Dict[int, Tree] = {}
    for workspace, ids in extract_windows().items():
      workspaces[workspace] = Tree.from_list(list(ids))

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

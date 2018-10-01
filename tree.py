from util import *
from typing import *

# a tree of splits
class Tree:
  def __str__(self):
    pass

  # return a set of ids contained in this tree
  def ids(self) -> Set[int]:
    pass

  # return a representation of the tree in rpn
  def rpn(self) -> str:
    pass

  # apply the window properties to the actual windows
  # all values range from 0.0 to 1.0
  def render(self, x:float, y:float, w:float, h:float):
    pass

  @staticmethod
  def from_list(l : List[int], vertical=True):
    if len(l) == 0:
      raise ValueError('from_list of empty list')
    if len(l) == 1:
      return Leaf(l[0])
    m = len(l) // 2
    return Split(
      Tree.from_list(l[:m], not vertical),
      Tree.from_list(l[m:], not vertical),
      vertical)

  @staticmethod
  def from_rpn(rpn:str):
    tokens = rpn.split()
    stack:List[Tree] = []
    i = 0
    while i < len(tokens):
      t = tokens[i]
      a = tokens[i + 1]
      if t == 'i':
        stack.append(Leaf(int(a)))
      elif t == 'v' or t == 'h':
        r = stack.pop()
        l = stack.pop()
        stack.append(Split(l, r, t == 'v', float(a)))
      i += 2
    if len(stack) != 1:
      raise ValueError('Failed to construct tree from rpn `{}`'.format(rpn))
    return stack[0]

# a window id
class Leaf(Tree):
  def __init__(self, id):
    self.id = id
    self.dirty = True # not yet rendered

  def __str__(self):
    return 'Leaf(' + hex(self.id) + ')'

  def ids(self) -> Set[int]:
    return set([self.id])

  def rpn(self) -> str:
    return '{} {}'.format('i', self.id)

  def render(self, x=0.0, y=0.0, w=1.0, h=1.0) -> None:
    if not self.dirty:
      return

    # maximize if root node taking up the whole screen
    maximize = is_close(x, 0.0) \
           and is_close(y, 0.0) \
           and is_close(w, 1.0) \
           and is_close(h, 1.0)
    run('wmctrl -i -r {} -b {},maximized_horz,maximized_vert'.format(
         self.id, 'add' if maximize else 'remove'))

    # if not taking up entire screen, set window to proper size
    if not maximize:
      run('wmctrl -i -r {} -e 0,{},{},{},{}'.format(
        self.id,
        int(x * screen_width),
        int(top_bar_height + y * screen_height),
        int(w * screen_width),
        int(h * screen_height - top_bar_height)))

    self.dirty = False

# a split of the rectangular region of the screen
class Split(Tree):
  def __init__(self, left, right, vertical=True, ratio=0.5):
    self.vertical = vertical
    self.ratio = ratio
    self.left = left
    self.right = right
    self.dirty = left.dirty or right.dirty

  def __str__(self) -> str:
    return '{}({}, {}, {})'.format(
      'Vertical' if self.vertical else 'Horizontal',
      self.ratio,
      self.left,
      self.right)

  def ids(self) -> Set[int]:
    return self.left.ids() | self.right.ids()

  def rpn(self) -> str:
    return '{} {} {} {}'.format(
      self.left.rpn(),
      self.right.rpn(),
      'v' if self.vertical else 'h',
      self.ratio)

  def render(self, left=0.0, top=0.0, width=1.0, height=1.0) -> None:
    if not self.dirty:
      return

    # compute (x1, y1, w1, h1) and (x2, y2, w2, h2) for the two children
    x1, y1 = left, top
    if self.vertical:
      h1 = h2 = height

      w1 = width * self.ratio
      w2 = width * (1 - self.ratio)

      x2 = x1 + w1
      y2 = y1
    else:
      h1 = height * self.ratio
      h2 = height * (1 - self.ratio)

      w1 = w2 = width

      x2 = x1
      y2 = y1 + h1

    self.left.render(x1, y1, w1, h1)
    self.right.render(x2, y2, w2, h2)
    self.dirty = False

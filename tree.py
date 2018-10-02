from util import *
from typing import *

# a window is an id and a bounding box (left, top, width, height)
Rectangle = Tuple[float, float, float, float]
Window = Tuple[int, Rectangle]

# a tree of splits
class Tree:
  def __str__(self):
    pass

  # an id and bounding box (id, (x, y, w, h)) for each leaf, given initial bounding box (x, y, w, h)
  def windows(self, x=0.0, y=0.0, w=1.0, h=1.0) -> Set[Window]:
    pass

  # mark as dirty
  def touch(self):
    pass

  # the set of ids contained in this tree
  def ids(self) -> Set[int]:
    return set(map(fst, self.windows()))

  # a representation of the tree in rpn
  def rpn(self) -> str:
    pass

  # (window id, area) of window with the largest area, assuming initial bounding box (w, h)
  def largest(self, best=None, w=1.0, h=1.0) -> Tuple[int, float]:
    pass

  # apply the window properties to the actual windows, assuming initial bounding box (x, y, w, h)
  # all values range from 0.0 to 1.0
  def render(self, x=0.0, y=0.0, w=1.0, h=1.0) -> None:
    pass

  # return an updated tree with a new window inserted
  def insert(self, i:int, vertical=True):
    max_id, _ = self.largest()

    def insert_at(a:Tree, vertical=True):
      if type(a) is Leaf:
        return (Split(a.touch(), Leaf(i).touch(), vertical), True) if a.id == max_id else (a, False)
      l, done = insert_at(a.left, not a.vertical)
      if done:
        return Split(l, a.right, a.vertical, a.ratio), True
      r, done = insert_at(a.right, not a.vertical)
      return Split(l, r, a.vertical, a.ratio), done

    return fst(insert_at(self))

  # return an updated tree with Leaf(i) deleted, unless its at the root
  def delete(self, i:int):
    pass

  # swap windows i, j in place
  def swap(self, i:int, j:int):
    pass

  # change the axis of the parent node holding window i
  def transpose(self, i:int):
    pass

  # helper for left_of, right_of, above, & below
  # return windows that satisfy a predicate f(x, y, w, h, x', y', w', h')
  #   x, y, w, h is geometry of window with id i
  #   x', y', w', h' is geometry of window being filtered
  def filter_on_window(self, i:int, pred) -> Set[Window]:
    if i not in self.ids():
      return set()
    windows = self.windows()
    #print('i =', i)
    _, rect = next(filter(lambda a: fst(a) == i, windows))
    result = set(filter(lambda a: fst(a) != i and pred(*rect, *snd(a)), windows))
    #print('result =', result)
    return result

  # windows to the left of the given id. empty set if the id is not in the tree
  def left_of(self, i:int) -> Set[Window]:
    return self.filter_on_window(i, lambda x, y, w, h, x1, y1, w1, h1: x1 + w1 <= x)

  # windows to the right of the given id
  def right_of(self, i:int) -> Set[Window]:
    return self.filter_on_window(i, lambda x, y, w, h, x1, y1, w1, h1: x + w <= x1)

  # windows above id
  def above(self, i:int) -> Set[Window]:
    return self.filter_on_window(i, lambda x, y, w, h, x1, y1, w1, h1: y1 + h1 <= y)

  # windows below id
  def below(self, i:int) -> Set[Window]:
    return self.filter_on_window(i, lambda x, y, w, h, x1, y1, w1, h1: y + h <= y1)

  # the nearest window to the given id, if it exists
  # if direction = 'right', compute distance btwn right edge of window i & left of candidate window
  # etc for the other directions
  def nearest(self, i:int, windows:Set[Window], direction:str) -> Union[Window, None]:
    if len(windows) == 0 or i not in self.ids():
      return None

    windows = self.windows()
    _, (x, y, w, h) = next(filter(lambda a: fst(a) == i, windows))
    def distance_to(window):
      _, (x1, y1, w1, h1) = window
      if not direction in {'left', 'right', 'above', 'below'}:
        raise ValueError('`{}` is not a valid direction'.format(direction))
      d = abs(
        x1 + w1 - x if direction == 'left' else
        x1 - (x + w) if direction == 'right' else
        (y1 + h1) - y if direction == 'above' else
        y1 - (y + h))
      return window, d

    return fst(min(map(distance_to, filter(lambda w: fst(w) != i, windows)), key=snd))

  # construct from list
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

  # construct from rpn (output of .rpn())
  @staticmethod
  def from_rpn(rpn:str):
    tokens = rpn.split()
    stack:List[Tree] = []
    i = 0
    while i < len(tokens):
      t = tokens[i]
      a = tokens[i + 1]
      dirty = int(tokens[i + 2]) == 1
      if t == 'i':
        stack.append(Leaf(int(a)))
      elif t == 'v' or t == 'h':
        r = stack.pop()
        l = stack.pop()
        stack.append(Split(l, r, t == 'v', float(a)))
      stack[-1].dirty = dirty
      i += 3
    if len(stack) != 1:
      raise ValueError('Failed to construct tree from rpn `{}`'.format(rpn))
    return stack[0]

# a window id
class Leaf(Tree):
  def __init__(self, id):
    self.id = id
    self.dirty = True # not yet rendered

  def __str__(self):
    return '{}Leaf({})'.format(
      '*' if self.dirty else '',
      hex(self.id))

  def windows(self, x=0.0, y=0.0, w=1.0, h=1.0) -> Set[Window]:
    return {(self.id, (x, y, w, h))}

  def touch(self):
    self.dirty = True
    return self

  def rpn(self) -> str:
    return '{} {} {}'.format('i', self.id, int(self.dirty))

  def largest(self, best=None, w=1.0, h=1.0) -> Tuple[int, float]:
    area = w * h
    if best is None:
      return self.id, area
    i, area2 = best
    return (self.id, area) if area >= area2 else best

  def render(self, x=0.0, y=0.0, w=1.0, h=1.0) -> None:
    if not self.dirty:
      return

    # maximize if root node taking up the whole screen
    maximize = is_close(x, 0.0) \
           and is_close(y, 0.0) \
           and is_close(w, 1.0) \
           and is_close(h, 1.0)
    run('wmctrl -i -r {} -b {},maximized_horz,maximized_vert'.format(
         hex(self.id), 'add' if maximize else 'remove'))

    # if not taking up entire screen, set window to proper size
    if not maximize:
      run('wmctrl -i -r {} -e 0,{},{},{},{}'.format(
        hex(self.id),
        int(x * screen_width),
        int(top_bar_height + y * screen_height),
        int(w * screen_width),
        int(h * screen_height - top_bar_height)))

    self.dirty = False

  def delete(self, i:int) -> Tree:
    return self

  def swap(self, i:int, j:int) -> None:
    if self.id == i:
      self.id = j
      self.touch()
    elif self.id == j:
      self.id = i
      self.touch()

  def transpose(self, i:int):
    pass

# a split of the rectangular region of the screen
class Split(Tree):
  def __init__(self, left, right, vertical=True, ratio=0.5):
    self.vertical = vertical
    self.ratio = ratio
    self.left = left
    self.right = right
    self.dirty = left.dirty or right.dirty

  def __str__(self) -> str:
    return '{}{}({}, {}, {})'.format(
      '*' if self.dirty else '',
      'Vertical' if self.vertical else 'Horizontal',
      self.ratio,
      self.left,
      self.right)

  def touch(self):
    self.dirty = True
    self.left.touch()
    self.right.touch()
    return self

  # compute (x1, y1, w1, h1) and (x2, y2, w2, h2) for the two children
  def subrects(self, left=0.0, top=0.0, width=1.0, height=1.0) -> Tuple[Rectangle, Rectangle]:

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

    return (x1, y1, w1, h1), (x2, y2, w2, h2)

  def windows(self, x=0.0, y=0.0, w=1.0, h=1.0) -> Set[Window]:
    (x1, y1, w1, h1), (x2, y2, w2, h2) = self.subrects(x, y, w, h)
    return self.left.windows(x1, y1, w1, h1) | self.right.windows(x2, y2, w2, h2)

  def rpn(self) -> str:
    return '{} {} {} {} {}'.format(
      self.left.rpn(),
      self.right.rpn(),
      'v' if self.vertical else 'h',
      self.ratio,
      int(self.dirty))

  def largest(self, best=None, w=1.0, h=1.0) -> Tuple[int, float]:
    (_, _, w1, h1), (_, _, w2, h2) = self.subrects(0, 0, w, h)
    return self.right.largest(self.left.largest(best, w1, h1), w2, h2)

  def render(self, left=0.0, top=0.0, width=1.0, height=1.0) -> None:
    if not self.dirty:
      return
    (x1, y1, w1, h1), (x2, y2, w2, h2) = self.subrects(left, top, width, height)
    self.left.render(x1, y1, w1, h1)
    self.right.render(x2, y2, w2, h2)
    self.dirty = False

  def delete(self, i:int) -> Tree:
    if type(self.left) is Leaf and self.left.id == i:
      return self.right.touch()
    if type(self.right) is Leaf and self.right.id == i:
      return self.left.touch()
    return Split(self.left.delete(i), self.right.delete(i), self.vertical, self.ratio)

  def swap(self, i:int, j:int) -> None:
    self.left.swap(i, j)
    self.right.swap(i, j)
    self.dirty = self.left.dirty or self.right.dirty

  def transpose(self, i:int) -> bool:
    transposable = lambda a: type(a) is Leaf and a.id == i
    if transposable(self.left) or transposable(self.right):
      self.left.touch()
      self.right.touch()
      self.vertical = not self.vertical
      self.dirty = True
      return True

    if not self.left.transpose(i):
      ok = self.right.transpose(i)
      self.dirty = self.left.dirty or self.right.dirty
      return ok

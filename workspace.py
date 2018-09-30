from util import *
from window import *
from typing import *

# multiple windows on the same screen
class Workspace:
  def __init__(self):
    self.windows = {} # map from window ids to Window instances

  # estimate the percentage of total pixels on the screen occupied by windows
  def area(self, samples=10000) -> float:
    from math import sqrt
    delta = sqrt(screen_pixels / samples)

    hits = 0
    for i in range(int(screen_width / delta)):
      for j in range(int(screen_height / delta)):
        left = int(i * delta)
        top = int(j * delta)
        hits += int(any(w.contains(left, top) for _, w in self.windows.items()))

    return hits / samples

  # apply the window properties to the actual window
  def render(self):
    from os import system

    # set maximize/unmaximize properly
    s = 'wmctrl -i -r {} -b {},maximized_horz,maximized_vert'
    system(s.format(self.id, 'add' if self.maximized else 'remove'))

    # if positions/sizes were fiddled with enough to be noticeable, adjust them irl
    if self.modified:
      s = 'wmctrl -i -r {} -e 0,{},{},{},{}'
      s = s.format(self.id, self.left, self.top, self.width, self.height)
      system(s)

    return self

if __name__ == '__main__':
  from time import time

  a = Workspace()
  a.windows[0] = Window(10, 10, 100, 100)

  n = 1000
  result = None
  start = time()
  for _ in range(n):
    result = a.area()
  elapsed = time() - start

  print('{} ms elapsed for {} samples ({} ms per), yielding {}'.format(
    round(elapsed, 3),
    n,
    round(elapsed / n, 3),
    result))
  

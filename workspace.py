from util import *
from window import *
from typing import *

# multiple windows on the same screen
class Workspace:
  def __init__(self):
    self.windows = {} # map from window ids to Window instances

  # estimate percentage of total pixels on the screen occupied by windows
  def area(self, samples=1000) -> float:
    from math import sqrt
    delta = sqrt(screen_pixels / samples)

    hits = 0
    for i in range(int(screen_width / delta)):
      for j in range(int(screen_height / delta)):
        left = int(i * delta)
        top = int(j * delta)
        hits += int(any(w.contains(left, top) for _, w in self.windows.items()))

    return hits / samples

  # estimate overlapped area relative to total no. of pixels on screen
  def overlap(self, samples=1000) -> float:
    return sum(w.area() for _, w in self.windows.items()) / screen_pixels \
         - self.area(samples)

  # apply the window properties to the actual windows
  def render(self):
    from os import system
    for id, w in self.windows.items():
      # maximize/unmaximize properly
      system('wmctrl -i -r {} -b {},maximized_horz,maximized_vert'.format(
        id, 'add' if w.maximized else 'remove'))

      # if positions/sizes were fiddled with enough to be noticeable, adjust them irl
      if w.adjusted():
        system('wmctrl -i -r {} -e 0,{},{},{},{}'.format(
          id, w.left, w.top, w.width, w.height))

    return self

if __name__ == '__main__':
  from time import time

  a = Workspace()
  a.windows[0] = Window(10, 10, 100, 100)

  n = 100
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
  
  print('Overlap = {}'.format(a.overlap()))

  a.windows[1] = Window(20, 20, 90, 90)
  print('New area = {}, new overlap = {}'.format(a.area(), a.overlap()))

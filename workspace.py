from util import *
from window import *
from typing import *

# multiple windows on the same screen
class Workspace:
  def __init__(self, windows={}):
    self.windows = {} # map from window ids to Window instances

  def __str__(self):
    return 'Workspace({ ' \
         + ', '.join('{}: {}'.format(i, w) for i, w in self.windows.items()) \
         + ' })'

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
    return max(sum(w.area() for _, w in self.windows.items()) - self.area(samples), 0)

  # return whether windows look "sufficiently tiled"
  def is_tiled(self) -> bool:
    area, overlap = self.area(), self.overlap()
    return area > 0.95 and overlap / area < 0.01

  # nudge/resize windows by a little bit in such a way that makes them more "tile-like"
  # while mostly preserving relative sizes and positions
  def step(self):
    # for each window, compute offsets for each edge
    crawls = {}
    for i, w in self.windows.items():
      crawls[i] = sum((w.get_crawl(v) for j, v in self.windows.items() if i != j), Crawl.empty)

    # adjust each window by the computed crawls
    print('Crawls = {}'.format(', '.join('{}: {}'.format(i, c) for i, c in crawls.items())))
    for i, w in self.windows.items():
      w.crawl(crawls[i])

    # expand each window to take up more space without overlapping with another window
    # speed of expansion along a particular dimension is proportional to size along that dimension

    return self

  # tile windows while preserving relative sizes and positions
  def tile(self, max_iterations=100):
    i = 0
    while not self.is_tiled() and i < max_iterations:
      print(self)
      self.step()
      i += 1
    print('Tiled after {} iterations'.format(i))
    return self

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
  a.windows[0].crawl(Crawl(5, 5, 5, 5))
  print(a.windows[0])

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

  a.tile()
  print('New area = {}, new overlap = {}'.format(a.area(), a.overlap()))
  print('New workspace = {}'.format(a))

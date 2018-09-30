from util import *
from typing import *

# position and dimensions of a single window
class Window:
  def __init__(self, left:int, top:int, width:int, height):
    # geometry/desktop
    self.left = left
    self.top = top
    self.width = width
    self.height = height

    self.maximized = False

    # original values (used to tell whether a major adjustment was made)
    self._left = left
    self._top = top
    self._width = width
    self._height = height

  # compute area relative to pixels on screen
  def area(self) -> float:
    return self.width * self.height / screen_pixels

  # compute overlap with another window
  def overlap(self, other) -> float:
    x1 = max(self.left, other.left)
    y1 = max(self.top, other.top)
    x2 = min(self.left + self.width, other.left + other.width)
    y2 = min(self.top + self.height, other.top + other.height)
    pixels = (x2 - x1) * (y2 - y1) if x1 < x2 and y1 < y2 else 0
    return pixels / screen_pixels

  # check whether a point is in the window
  def contains(self, left, top) -> bool:
    return self.left <= left and left <= self.left + self.width \
       and self.top <= top and top <= self.top + self.height

  # maximize
  def maximize(self):
    self.maximized = True
    return self

  # unmaximize
  def unmaximize(self):
    self.maximized = False
    return self

  # move top-left corner to coordinates (left, top)
  def move(self, left:int, top:int):
    left = clamp_x(left)
    top = clamp_y(top)
    self.left = left
    self.top = top
    return self

  # shift top-left corner by offsets (left, top)
  def nudge(self, left:int, top:int):
    return self.move(self.left + left, self.top + top)

  # resize to new width & height
  def resize(self, width:int, height:int):
    width = clamp_width(self.width, self.left)
    height = clamp_height(self.height, self.top)
    self.width = width
    self.height = height
    return self

  # shift dimensions by width and height
  def stretch(self, width:int, height:int):
    return self.resize(self.width + width, self.height + height)

  # check whether a major adjustment was made
  def adjusted(self) -> bool:
    return not is_close(left, self._left) \
        or not is_close(top, self._top) \
        or not is_close(width, self._width) \
        or not is_close(height, self._height)

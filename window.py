from util import *
from typing import *

# window data structure
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
    return is_close(left, self._left)
        or is_close(top, self._top)
        or is_close(width, self._width)
        or is_close(height, self._height)

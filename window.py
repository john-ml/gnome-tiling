from typing import *

# screen resolution
def dimensions(dim:int) -> int:
  import os
  s = "xdpyinfo | awk '/dimensions/{print $2}' | sed 's/x/ /' | awk '//{print $%d}'" % (dim + 1)
  return int(os.popen(s).read())
screen_width = dimensions(0)
screen_height = dimensions(1)
del dimensions

# clamp an x coordinate by screen width
def clamp_x(x:int) -> int:
  return min(max(x, 0), screen_width)

# clamp a y coordinate by screen height
def clamp_y(y:int) -> int:
  return min(max(y, 0), screen_height)

# clamp a width by screen resolution & left margin 
def clamp_width(width:int, left:int) -> int:
  return min(max(width, 0), screen_width - left)

# clamp a height by screen resolution & top margin
def clamp_height(height:int, top:int) -> int:
  return min(max(height, 0), screen_height - top)

# check if two values are "close enough".
# if so, don't need to issue a wmctrl command to adjust 
def is_close(a:int, b:int) -> bool:
  return a == b

# window data structure
class Window:
  def __init__(self, id:int, desktop:int, left:int, top:int, width:int, height):
    self.id = id

    # geometry/desktop
    self.desktop = desktop
    self.left = left
    self.top = top
    self.width = width
    self.height = height

    self.maximized = False
    self.modified = False

    # original values (used to tell whether a wmctrl command is needed in .render())
    self._desktop = desktop
    self._left = left
    self._top = top
    self._width = width
    self._height = height

  # maximize
  def maximize(self):
    self.modified = self.modified or not self.maximized
    self.maximized = True
    return self

  # unmaximize
  def unmaximize(self):
    self.modified = self.modified or self.maximized
    self.maximized = False
    return self

  # move to desktop
  def send(self, desktop:int):
    self.modified = self.modified
                    or desktop != self._desktop
    self.desktop = desktop
    return self

  # move top-left corner to coordinates (left, top)
  def move(self, left:int, top:int):
    left = clamp_x(left)
    top = clamp_y(top)
    self.modified = self.modified
                    or is_close(left, self._left)
                    or is_close(top, self._top)
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
    self.modified = self.modified
                    or is_close(width, self._width)
                    or is_close(height, self._height)
    self.width = width
    self.height = height
    return self

  # shift dimensions by width and height
  def stretch(self, width:int, height:int):
    return self.resize(self.width + width, self.height + height)


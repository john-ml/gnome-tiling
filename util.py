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

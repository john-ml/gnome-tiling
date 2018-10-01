from typing import *

DEBUG = True

# hard-coded constant for my computer # TODO figure out how to detect this?
# the height of the top bar and title bars
top_bar_height = 27

# screen resolution
def dimensions(dim:int) -> int:
  from os import popen
  s = "xdpyinfo | awk '/dimensions/{print $2}' | sed 's/x/ /' | awk '//{print $%d}'" % (dim + 1)
  return int(popen(s).read())
screen_width = dimensions(0)
screen_height = dimensions(1) - top_bar_height
screen_pixels = screen_width * screen_height
del dimensions

# check if two values are "close enough".
def is_close(a:float, b:float) -> bool:
  return abs(a - b) < 0.01

# run a shell command
def run(s:str) -> None:
  from os import system
  if DEBUG:
    print(s)
  system(s)

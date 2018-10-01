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

# extract { workspace number: [window id] } using wmctrl
def extract_windows() -> Dict[int, List[int]]:
  from os import popen

  # extract window information
  # output is 1 line per window, containing:
  #   id workspace left top width height username title
  # just need id & workspace
  s = 'wmctrl -l -G'
  if DEBUG:
    print(s)
  entries = (l.split() for l in popen(s).read().split('\n'))

  # need to filter out:
  #   the empty list from the newline at the end of the input
  #   the Desktop "window" that shows up and takes up all of workspace 0
  entries = filter(lambda a: len(a) >= 8 and not ' '.join(a[7:]) == 'Desktop', entries)

  # construct workspace dict
  workspaces:Dict[int, List[int]] = {}
  for entry in entries:
    id, workspace = int(entry[0], 16), int(entry[1], 16)
    if workspace not in workspaces:
      workspaces[workspace] = [id]
    else:
      workspaces[workspace].append(id)

  return workspaces

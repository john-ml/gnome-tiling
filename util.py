# hard-coded constant for my computer # TODO figure out how to detect this?
# the height of the top bar and title bars
top_bar_height = 27

# screen resolution
def dimensions(dim:int) -> int:
  import os
  s = "xdpyinfo | awk '/dimensions/{print $2}' | sed 's/x/ /' | awk '//{print $%d}'" % (dim + 1)
  return int(os.popen(s).read())
screen_width = dimensions(0)
screen_height = dimensions(1) - top_bar_height
screen_pixels = screen_width * screen_height
del dimensions

# check if two values are "close enough".
def is_close(a:float, b:float) -> bool:
  return abs(a - b) < 0.01

# run a shell command
def run(s:str, debug=False) -> None:
  from os import system
  if debug:
    print(s)
  system(s)

# extract { workspace number: [window id] } using wmctrl
def extract_windows(debug=False) -> None:
  from os import popen

  # extract window information
  # output is 1 line per window, containing:
  #   id workspace left top width height username title
  # just need id & workspace
  s = 'wmctrl -l -G'
  if debug:
    print(s)
  entries = (l.split() for l in popen(s).read().split('\n'))

  # need to filter out:
  #   the empty list from the newline at the end of the input
  #   the Desktop "window" that shows up and takes up all of workspace 0
  entries = filter(lambda a: len(a) >= 8 and not ' '.join(a[7:]) == 'Desktop', entries)

  # construct workspace dict
  workspaces = {}
  for entry in entries:
    id, workspace = entry[:2]
    if workspace not in workspaces:
      workspaces[workspace] = [id]
    else:
      workspaces[workspace].append(id)

  return workspaces

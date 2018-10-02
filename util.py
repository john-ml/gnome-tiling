from typing import *

DEBUG = True

# hard-coded constant for my computer # TODO figure out how to detect this?
# the height of the top bar and title bars
top_bar_height = 27

# run a shell command and get stdout
def run(s:str) -> str:
  from os import popen
  if DEBUG:
    print(s)
  return popen(s).read()

# screen resolution
def dimensions(dim:int) -> int:
  return int(run(
    "xdpyinfo | awk '/dimensions/{print $2}' | sed 's/x/ /' | awk '//{print $%d}'" % (dim + 1)))
screen_width = dimensions(0)
screen_height = dimensions(1) - top_bar_height
screen_pixels = screen_width * screen_height
del dimensions

# check if two values are "close enough".
def is_close(a:float, b:float) -> bool:
  return abs(a - b) < 0.01

# get workspace and id of active window
def active_window() -> Union[Tuple[int, int], None]:
  i = int(run('xdotool getactivewindow'))
  try:
    for l in run('wmctrl -l').split('\n'):
      tokens = l.split()
      if int(tokens[0], 16) == i:
        return i, int(tokens[1])
  except:
    return None

# focus a window id
def focus_window(i:int) -> None:
  run('wmctrl -i -a {}'.format(hex(i)))

# eh
fst = lambda a: a[0]
snd = lambda a: a[1]

# eh!
def option_map(f, a:Union[Any, None]) -> Any:
  return f(a) if a is not None else None

# get id and desktop for all windows
def extract_windows() -> Dict[int, Set[int]]:
  # extract window information
  # output is 1 line per window, containing:
  #   id workspace left top width height username title
  # just need id & workspace
  entries = (l.split() for l in run('wmctrl -l -G').split('\n'))

  # need to filter out:
  #   the empty list from the newline at the end of the input
  #   the Desktop "window" that shows up and takes up all of workspace 0
  entries = filter(lambda a: len(a) >= 8 and not ' '.join(a[7:]) == 'Desktop', entries)

  # construct workspace dict
  result:Dict[int, Set[int]] = {}
  for entry in entries:
    i, workspace = int(entry[0], 16), int(entry[1], 16)
    if workspace not in result:
      result[workspace] = {i}
    else:
      result[workspace] |= {i}

  return result

from typing import *

DEBUG = True

# hard-coded constant for my computer # TODO figure out how to detect this?
# the height of the top bar and title bars
top_bar_height = 0

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

# wm class given id
def wm_classes(id:int) -> List[str]:
  classes = run(f'xprop -id {hex(id)} | grep WM_CLASS')
  return list(eval(classes[classes.index('=')+1:].strip())) # meh

# sometimes, decorations make dimensions inaccurate.
# get left border width, right border width, title bar width, and bottom border width
def frame_extents(id:int) -> Union[Tuple[int, int, int, int], None]:
  try:
    l, r, t, b = tuple(map(int, run(' | '.join([
      f'xprop -id {hex(id)}',
      "grep '_FRAME_EXTENTS'",
      "sed -E 's/.*_FRAME_EXTENTS.*= ([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+)/\\1 \\2 \\3 \\4/'"])).split()))
    return l, r, t, b
  except ValueError:
    return None

# get x, y, w, h of a window using wmctrl
def wmctrl_region(id:int) -> Tuple[int, int, int, int]:
  # {10} to pad resulting string to 10 chars long ==> 8 hex digits
  return tuple(map(int,
    run(f'''wmctrl -lG | awk '/{id:#0{10}x}/{{print $3" "$4" "$5" "$6}}' ''').split()))

# get x, y, w, h of a window using xwininfo
def xwininfo_region(id:int) -> Tuple[int, int, int, int]:
  # {10} to pad resulting string to 10 chars long ==> 8 hex digits
  x = int(run(f"xwininfo -id {hex(id)} | grep 'Absolute upper-left X:'").split(':')[1])
  y = int(run(f"xwininfo -id {hex(id)} | grep 'Absolute upper-left Y:'").split(':')[1])
  w = int(run(f"xwininfo -id {hex(id)} | grep 'Width:'").split(':')[1])
  h = int(run(f"xwininfo -id {hex(id)} | grep 'Height:'").split(':')[1])
  return x, y, w, h

# sometimes, decorations make wmctrl's dimensions inaccurate.
# get x, y, w, h of the opaque region of the window with given id
def opaque_region(id:int) -> Union[Tuple[int, int, int, int], None]:
  try:
    x, y, w, h = tuple(map(int, run(
      f'xprop _NET_WM_OPAQUE_REGION -id {hex(id)}' +
      " | sed -E 's/.*= ([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+)/\\1 \\2 \\3 \\4/'").split()))
    return x, y, w, h
  except ValueError:
    return None

# check if two values are "close enough".
def is_close(a:float, b:float) -> bool:
  return abs(a - b) < 0.001

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

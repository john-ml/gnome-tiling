# command line utility to manage tiled windows
from util import *
from manager import *
import sys

# print help thing
def print_usage():
  print('\n'.join([
    'Usage: python3 tile.py [{}]'.format(' | '.join([
      'init',
      'refresh',
      'list',
      'close',
      'transpose',
      'move <workspace>',
      'focus <direction>',
      'swap <direction>',
      'terminal'])),
    '  direction = left | right | above | below',
    '  workspace = [1-10]']))

if __name__ == '__main__':
  from pathlib import Path
  import pickle
  # to store the window state
  stash = str(Path.home()) + '/.tile/configuration'
  # to store discrepancies
  err = str(Path.home()) + '/.tile/errata'

  try:
    with open(err, 'rb') as f:
      errata, incomplete_report = pickle.load(f)
  except FileNotFoundError:
    errata, incomplete_report = dict(), None
  print(f'errata = {errata}')
  print(f'incomplete_report = {incomplete_report}')

  if len(sys.argv) == 1:
    print_usage()
    exit()

  def die():
    open(stash, 'w').write(repr(manager))
    with open(err, 'wb') as f:
      pickle.dump((errata, incomplete_report), f)
    exit()

  option = sys.argv[1]

  # force tile all windows & initialize stash
  if option == 'init':
    manager = Manager.from_reality(errata)
    manager.render()
    die()

  if not Path(stash).is_file():
    print('Error: `{}` does not exist yet'.format(stash))
    print('Run `python3 tile.py init` first')
    exit()

  with open(stash, 'r') as f:
    manager = Manager.from_str(errata, f.read())

  # account for new windows/deleted windows
  if option == 'refresh':
    manager.refresh()

  # list the workspace trees
  elif option == 'list':
    print(manager)
    #for _, workspace in manager.workspaces.items():
    #  print(workspace.windows())

  # close focused window
  elif option == 'close':
    manager.close()

  # transpose focused window
  elif option == 'transpose':
    manager.transpose()

  # shift focus
  elif option == 'focus':
    if len(sys.argv) < 3:
      print('Missing direction argument to `focus`')
      die()
    try:
      manager.focus(sys.argv[2])
    except ValueError as e:
      print(e)

  # swap focused window position
  elif option == 'swap':
    if len(sys.argv) < 3:
      print('Missing direction argument to `swap`')
      die()
    try:
      manager.swap(sys.argv[2])
    except ValueError as e:
      print(e)

  # move active window to a different workspace
  elif option == 'move':
    if len(sys.argv) < 3:
      print('Missing direction argument to `move`')
      die()
    try:
      manager.move(int(sys.argv[2]) - 1)
    except ValueError as e:
      print(e)

  elif option == 'open_report':
    id = int(run("xwininfo | awk '/Window id/{print $4}'"), 16)
    incomplete_report = xwininfo_region(id)

  elif option == 'close_report':
    if incomplete_report is None:
      print('No report to close')
      die()
    id = int(run("xwininfo | awk '/Window id/{print $4}'"), 16)
    oldx, oldy, oldw, oldh = incomplete_report
    newx, newy, neww, newh = xwininfo_region(id)
    print('old:', oldx, oldy, oldw, oldh)
    print('new:', newx, newy, neww, newh)
    dx = newx - oldx
    dy = newy - oldy
    dw = neww - oldw
    dh = newh - oldh
    print('delta:', dx, dy, dw, dh)
    for s in wm_classes(id):
      if s in errata:
        x, y, w, h = errata[s] # add to old delta
        errata[s] = (x + dx, y + dy, w + dw, h + dh)
      else:
        errata[s] = (dx, dy, dw, dh)
    incomplete_report = None

  # open a terminal window
  elif option == 'terminal':
    run('x-terminal-emulator')
    manager.refresh()

  else:
    print('Unrecognized option `{}`'.format(option))
    print_usage()

  die() # save changes for next run

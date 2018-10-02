# gnome-tile

Command-line utility for pretending that GNOME is a tiling window manager.

Requires: `xdotool` `wmctrl` `xdpyinfo` `awk` `sed`

### Usage

`python3 tile.py [init | refresh | list | close | transpose | move <workspace> | focus <direction> | swap <direction> | terminal]` where
- `direction = left | right | above | below`
- `workspace = 1 .. 10`

To use as a "window manager," just make keybindings for the various actions.

### Actions

`init`: force window tiling and store initial configuration in `~/.tiling_configuration`

`refresh`: tile newly created windows & remove windows that were closed since last refresh; store changes in `~/.tiling_configuration`

`list`: pretty-print stored configuration

`close`: close active window

`transpose`: swap the splitting orientation of active window (i.e. horizontal -> vertical & vice versa)

`move n`: move the active window to the `n`th workspace

`focus d`: shift focus in the given direction

`swap d`: swap active window with the nearest window in the given direction

`terminal`: open a terminal window


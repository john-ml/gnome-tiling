
  # apply the window properties to the actual window
  def render(self):
    from os import system

    # set maximize/unmaximize properly
    s = 'wmctrl -i -r {} -b {},maximized_horz,maximized_vert'
    system(s.format(self.id, "add" if self.maximized else "remove"))

    # if positions/sizes were fiddled with enough to be noticeable, adjust them irl
    if self.modified:
      s = 'wmctrl -i -r {} -e 0,{},{},{},{}'
      s = s.format(self.id, self.left, self.top, self.width, self.height)
      system(s)

    return self

"""https://code.activestate.com/recipes/134892/
"""

# pyright: reportUnusedImport=none, reportMissingImports=none
# pylint: disable=import-outside-toplevel,unused-import,import-error,pointless-statement


class Getch:
    """Gets a single character from standard input. Does not echo to the screen"""

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchUnix()
            except ImportError:
                self.impl = _GetchMacCarbon()

    def __call__(self):
        return self.impl()


class _GetchUnix:
    def __init__(self):
        # import termios now or else you'll get the Unix version on the Mac
        import sys
        import termios
        import tty

    def __call__(self):
        import sys
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt
        import sys

    def __call__(self):
        import msvcrt
        import sys

        sys.stdin.reconfigure(encoding="utf-8")
        char = msvcrt.getch()
        try:
            return char.decode("utf-8")
        except:
            return char


class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """

    def __init__(self):
        import Carbon

        Carbon.Evt  # see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon

        if Carbon.Evt.EventAvail(0x0008)[0] == 0:  # 0x0008 is the keyDownMask
            return ""
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            _, msg, _, _, _ = Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

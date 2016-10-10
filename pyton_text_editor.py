#!/usr/bin/python3

import sys # for access to stdin
import tty # for setting tty input to raw
import termios # for restoring the default tty behavior when done

from sys import stdout # for doing raw terminal output

KEY_CTRL_U = "^P"
#KEY_CTRL_D = 
#KEY_CTRL_F = 
#KEY_CTRL_B = 

class State:
    def __init__(self, buffer, cursor):
        self.buffer = buffer
        self.cursor = cursor

    @staticmethod
    def blank():
        return State([""], Cursor.blank())

# end class State

class Cursor:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    @staticmethod
    def blank():
        return Cursor(0, 0)

    # methods for moving cursor in cardinal directions
    def up(self): return Cursor(self.row - 1, self.col)
    def down(self): return Cursor(self.row + 1, self.col)
    def left(self): return Cursor(self.row, self.col - 1)
    def right(self): return Cursor(self.row, self.col + 1)

# end class Cursor

class Editor:

    # called on entry of with
    def __enter__(self):
        # get the current tty settings so we can restore them later
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

        # set the tty to raw input mode to process keys directly
        tty.setraw(sys.stdin) 
        return self

    def main(self):
        state = State.blank() # start with a blank screen/empty buffer
        while True:
            state = self.read_char(state)
            self.render(state)
        # end while
    # end def main

    def read_char(self, state):
        ch = sys.stdin.read(1)

        if ch == '\x03':
            sys.exit(0)
        elif ch == '\r':
           return self.newline(state)
        else:
            return self.process_keystroke(state, ch)

    # end def read_char():

    def newline(self, state):
        return State(state.buffer + ['loooootsa letters'],
                     state.cursor)

    def process_keystroke(self, state, ch):
        line = state.buffer[0]
        line += ch
        return State([line],
                     state.cursor)

    def render(self, state): 
        stdout.write(ANSI.clear())
        stdout.write(ANSI.move_cursor(0, 0))
        for line in state.buffer:
            stdout.write(line)
            stdout.write(ANSI.cursor_down())
        stdout.flush()

    # end def render()

    # called on exit of with
    def __exit__(self, ext_type, exc_value, traceback):
        # restore term settings
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings) 

# end class Editor

class ANSI:
    ESC = chr(27)

    @staticmethod
    def escape(sequence):
        return ANSI.ESC + "[" + sequence


    @staticmethod
    def clear():
        return ANSI.escape("2J")

    @staticmethod
    def move_cursor(row, col):
        return ANSI.escape(str(row)+';'+str(col)+'H')

    @staticmethod
    def cursor_down(lines=1):
        return ANSI.escape(str(lines)+ 'B')

    @staticmethod
    def cursor_up(lines=1):
        return ANSI.escape(str(lines)+ 'B')

    @staticmethod
    def cursor_left(lines=1):
        return ANSI.escape(str(lines)+ 'B')

    @staticmethod
    def cursor_right(lines=1):
        return ANSI.escape(str(lines)+ 'B')

# end class ANSI

if __name__ == "__main__":
    with Editor() as e:
        e.main()
# eof

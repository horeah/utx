import ctypes
from ctypes import Structure, c_short, pointer
from ctypes.wintypes import BOOL, WORD, DWORD
global stdout_handle
stdout_handle = ctypes.windll.kernel32.GetStdHandle(-11)


class COORD(Structure):
    _fields_ = [('X', c_short),
                ('Y', c_short)]


class SMALL_RECT(Structure):
    _fields_ = [('Left', c_short),
                ('Top', c_short),
                ('Right', c_short),
                ('Bottom', c_short)]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [('size', COORD),
                ('cursorPosition', COORD),
                ('attributes', WORD),
                ('window', SMALL_RECT),
                ('maxWindowSize', COORD)]


def get_cursor():
    """Get the current cursor position"""
    buffer_info = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(stdout_handle, pointer(buffer_info))
    return (buffer_info.cursorPosition.X, buffer_info.cursorPosition.Y)


def move_cursor(x, y):
    """Move the cursor to the specified location"""
    location = COORD(x, y)
    ctypes.windll.kernel32.SetConsoleCursorPosition(stdout_handle, location)


def get_buffer_size():
    """Get the size of the text buffer"""
    buffer_info = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(stdout_handle, pointer(buffer_info))
    return (buffer_info.size.X, buffer_info.size.Y)


def cursor_backward(count):
    """Move cursor backward with the given number of positions"""
    (x, y) = get_cursor()
    while count > 0:
        x -= 1
        if x < 0:
            y -= 1
            (x, _) = get_buffer_size()
            x -= 1
        count -= 1
    move_cursor(x, y)

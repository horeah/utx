"""
Miscellaneous utility functions
"""

import sys, time, signal

def format_size(bytes, pretty = False):
    """
    Format an int size (in bytes) into a string.
    Optionally, an eye-friendly formatting can be used
    """
    if pretty:
        if bytes < 1024:
            return str(bytes)
        elif bytes < 1024 * 1024:
            return '%.1fK' % (bytes / 1024.0)
        elif bytes < 1024 * 1024 * 1024:
            return '%.1fM' % (bytes / (1024 * 1024.0))
        else:
            return '%.1fG' % (bytes / (1024 * 1024 * 1024.0))
    else:
        return str(bytes)


def format_time(seconds, pretty = False):
    """
    Format a time value (given in seconds from the Epoch) into a string.
    If the pretty flag is set, a human-readable format is used
    """
    if pretty:
        if time.localtime(seconds).tm_year == time.localtime().tm_year:
            format = '%b %d %H:%M'
        else:
            format = '%Y %b %d'
        return time.strftime(format, time.localtime(seconds))
    else:
        return str(int(seconds))


def exit_on_ctrl_c(signum, frame):
    """
    Signal handler that catches SIGINT and terminates the program
    """
    if signum == signal.SIGINT:
        print('^C')
        sys.exit(1)

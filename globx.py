"""
Utility functions related to globbing and pattern matching
"""

import sys, os, fnmatch, time

# Special directory entries, needing special treatment in some situations
special_entries = ['.', '..']


def globx(directory, pattern):
    """Recursive glob in a directory based on a globbing pattern"""
    if pattern == '':
        return
        
    (elem, _, rest) = pattern.partition('\\')
    files = os.listdir(directory)
    if elem == '**':
        for f in files:
            if os.path.isdir(directory + '\\' + f):
                for g in globx(directory + '\\' + f, pattern):
                    yield f + '\\' + g
        for g in globx(directory, rest):
            yield g
    else:
        for f in special_entries + files:
            if matches(f, elem):
                if rest == '' and not f in special_entries:
                    yield f
                if os.path.isdir(directory + '\\' + f):
                    for g in globx(directory + '\\' + f, rest):
                        yield f + '\\' + g


def matches(name, pattern):
    """
    Check if a filename matches a pattern.
    As opposed to the regular fnmatch.fnmatch(), this ensures exact matches for 
    the special directory entries ('.' and '..')
    """
    if name in special_entries:
        return name == pattern
    else:
        return fnmatch.fnmatch(name, pattern)


def split_target(arg):
    """
    Split a string argument into a directory part and a pattern part.
    The directory part can be empty -- the current directory should be used in this case
    """
    sep_idx = arg.find('\\\\')
    if sep_idx >= 0:
        # Base directory provided via marker
        directory = arg[:sep_idx]
        if len(directory) == 2 and directory[1] == ':':
            directory += '\\'
        pattern = arg[sep_idx + 2:]
    else:
        # No base directory defined
        wildcard_idx = arg.find('*')
        if wildcard_idx < 0:
            wildcard_idx = arg.find('?')
        if wildcard_idx >= 0:
            # Wildcard found
            directory = os.path.dirname(arg[:wildcard_idx])
            pattern = arg[wildcard_idx:]
        else:
            # No wildcard found
            (directory, pattern) = os.path.split(arg)
    return (directory, pattern)


def is_recursive(pattern):
    """Check whether a pattern contains a recursive wildcard"""
    return pattern.find('**') >= 0


def is_glob(pattern):
    """Check whether a pattern contains a globbing"""
    return pattern.find('*') >= 0 or pattern.find('?') >= 0

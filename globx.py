import sys, os, fnmatch, time

special_entries = ['.', '..']

def globx(directory, pattern):
#    print [directory, pattern]
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
    if name in special_entries:
        return name == pattern
    else:
        return fnmatch.fnmatch(name, pattern)

def format_size(bytes, pretty = False):
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
    if pretty:
        if time.localtime(seconds).tm_year == time.localtime().tm_year:
            format = '%b %d %H:%M'
        else:
            format = '%Y %b %d'
        return time.strftime(format, time.localtime(seconds))
    else:
        return str(int(seconds))

def split_target(arg):
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
    return pattern.find('**') >= 0

def is_glob(pattern):
    return pattern.find('*') >= 0 or pattern.find('?') >= 0

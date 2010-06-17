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
            if fnmatch.fnmatch(f, elem):
                if rest == '' and not f in special_entries:
                    yield f
                if os.path.isdir(directory + '\\' + f):
                    for g in globx(directory + '\\' + f, rest):
                        yield f + '\\' + g

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



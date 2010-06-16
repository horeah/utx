import sys, os, fnmatch

def globx(directory, pattern):
#    print [directory, pattern]
    if pattern == '':
        return []
    (elem, _, rest) = pattern.partition('\\')
    files = os.listdir(directory)
    results = []
    if elem == '**':
        for f in files:
            if os.path.isdir(directory + '\\' + f):
                results += [f + '\\' + g for g in globx(directory + '\\' + f, pattern)]
        results += globx(directory, rest)
    else:
        for f in files:
            if fnmatch.fnmatch(f, elem):
                if rest == '':
                    results += [f]
                if os.path.isdir(directory + '\\' + f):
                    results += [f + '\\' + g for g in globx(directory + '\\' + f, rest)]
    return results

def globxy(directory, pattern):
#    print [directory, pattern]
    if pattern == '':
        return
        
    (elem, _, rest) = pattern.partition('\\')
    files = os.listdir(directory)
    results = []
    if elem == '**':
        for f in files:
            if os.path.isdir(directory + '\\' + f):
                for g in globxy(directory + '\\' + f, pattern):
                    yield f + '\\' + g
        for g in globxy(directory, rest):
            yield g
    else:
        for f in files:
            if fnmatch.fnmatch(f, elem):
                if rest == '':
                    yield f
                if os.path.isdir(directory + '\\' + f):
                    for g in globxy(directory + '\\' + f, rest):
                        yield f + '\\' + g

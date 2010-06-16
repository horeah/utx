import sys, globx, optparse, os


def main():
    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'lsx [options] <files>',
                                   version = '10.1')
    parser.add_option('-l', '--long', 
                      action = 'store_true', dest = 'long_format', 
                      default = False,
                      help = 'display detailed file information')
    parser.add_option('-p', '--pretty',
                      action = 'store_true', dest = 'pretty_print',
                      default = False,
                      help = 'show human-readable file sizes')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    if len(args) == 0:
        directory = '.'
        pattern = '**\*'
    elif len(args) == 1:
        sep_idx = args[0].find('\\\\')
        if sep_idx >= 0:
            directory = args[0][:sep_idx]
            pattern = args[0][sep_idx + 2:]
        else:
            directory = '.'
            pattern = args[0]

    if options.verbose:
        print '>> Listing "' + pattern + '" based at "' + directory + '":'

    col_width = 12
    col_spacing = 4

    results = globx.globx(directory, pattern)
    for elem in results:
        line = elem
        if options.long_format:
            # Size
            try:
                size_str = globx.format_size(os.path.getsize(directory + '\\' + elem), options.pretty_print)
            except os.error:
                size_str = '??'
            sys.stdout.write(' ' * (col_width - len(size_str)))
            sys.stdout.write(size_str)
            sys.stdout.write(' ' * col_spacing)
            
            # Modification time
            try:
                mtime_str = globx.format_time(os.path.getmtime(directory + '\\' + elem), options.pretty_print)
            except os.error:
                mtime_str = '??'
            sys.stdout.write(' ' * (col_width - len(mtime_str)))
            sys.stdout.write(mtime_str)
            sys.stdout.write(' ' * col_spacing)
        print line

if __name__ == '__main__':
    main()

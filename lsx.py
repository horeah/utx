#
# Equivalent of a friendlier, recursive version of ls
#
# List (recursively) files that match a given pattern; listed names can start at
# a specified base directory.
#
# Author: Horea Haitonic
#

import sys, globx, util, optparse, os, itertools, signal
from sys import stdout


def main():
    # Prevent stacktraces on Ctrl-C
    signal.signal(signal.SIGINT, util.exit_on_ctrl_c)

    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'lsx [options] <pattern>',
                                   description = 
"""List (recursively) files and directories that match a given pattern.
You can use the well-known '*' and '?' as expected, '**' to recursively
match subdirectories and a '\\\\' (double backslash) to mark the base
directory. If no pattern is provided, '.\\\\**\\*' is implied.""",
                                   version = '0.2')
    parser.add_option('-x', '--exclude', 
                      action = 'append', type='string', dest = 'exclude_list', 
                      metavar = 'PATTERN',
                      default = [],
                      help = 'exclude files matching pattern')
    parser.add_option('-X', '--exclude-ending', 
                      action = 'append', type='string', dest = 'exclude_list_ending', 
                      metavar = 'PATTERN',
                      default = [],
                      help = 'exclude files ending in pattern')
    parser.add_option('-l', '--long', 
                      action = 'store_true', dest = 'long_format', 
                      default = False,
                      help = 'display detailed file information')
    parser.add_option('-p', '--pretty',
                      action = 'store_true', dest = 'pretty_print',
                      default = False,
                      help = 'show details in human-readable format')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # Interpret the <files> argument
    if len(args) == 0:
        # No pattern given, use the implicit '.\\**\*'
        directory = '.'
        pattern = '**\\*'
    else:
        target = args[0].replace('/', '\\')
        (directory, pattern) = globx.split_target(target)
        if directory == '':
            directory = '.'

    if not globx.is_glob(pattern) and os.path.isdir(directory + '\\' + pattern):
        directory += '\\' + pattern
        pattern = '**\\*'
    
    if options.verbose:
        print '>> Listing "' + pattern + '" based at "' + directory + '":'
        for exclude in options.exclude_list:
            print '>>   Excluding entries matching "' + exclude + '"'
        for exclude in options.exclude_list_ending:
            print '>>   Excluding entries ending in "' + exclude + '"'

    col_width = 12      # Size of a display column
    col_spacing = 4     # Spacing b/w columns

    results = globx.globx(directory, pattern)
    filtered_results = itertools.ifilter(
        lambda x: 
        [e for e in options.exclude_list if globx.matches_path(x, e)] == [] and \
        [e for e in options.exclude_list_ending if globx.matches_path(x, e, True)] == [],
        results)

    for elem in filtered_results:
        if options.long_format:
            # Size
            try:
                size_str = util.format_size(os.path.getsize(directory + '\\' + elem), options.pretty_print)
            except os.error:
                size_str = '??'
            stdout.write(' ' * (col_width - len(size_str)))
            stdout.write(size_str)
            stdout.write(' ' * col_spacing)
            
            # Modification time
            try:
                mtime_str = util.format_time(os.path.getmtime(directory + '\\' + elem), options.pretty_print)
            except os.error:
                mtime_str = '??'
            stdout.write(' ' * (col_width - len(mtime_str)))
            stdout.write(mtime_str)
            stdout.write(' ' * col_spacing)
        print elem


# Entry point
if __name__ == '__main__':
    main()

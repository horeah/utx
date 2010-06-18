#
# Equivalent of a friendlier, recursive version of ls
#
# List (recursively) files that match a given pattern; listed names can start at
# a specified base directory.
#
# Author: Horea Haitonic
#

import sys, globx, optparse, os


def main():
    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'lsx [options] <pattern>',
                                   description = 
"""List (recursively) files that match a given pattern.
You can use the well-known '*' and '?' as expected, '**' to recursively
match subdirectories and a '\\\\' (double backslash) to mark the base
directory. If no pattern is provided, '.\\\\**\\*' is implied.""",
                                   version = '10.1')
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
        pattern = '**\*'
    elif len(args) == 1:
        sep_idx = args[0].find('\\\\')
        if sep_idx >= 0:
            # Base directory provided via marker
            directory = args[0][:sep_idx]
            if len(directory) == 2 and directory[1] == ':':
                directory += '\\'
            pattern = args[0][sep_idx + 2:]
        else:
            # No base directory defined -- infer based on the type of path
            if os.path.isabs(args[0]):
                star_idx = args[0].find('*')
                if star_idx < 0:
                    directory = args[0]
                    pattern = '**\*'
                else:
                    directory = args[0][:star_idx]
                    pattern = args[0][star_idx:]
            else:
                directory = '.'
                pattern = args[0]

    if options.verbose:
        print '>> Listing "' + pattern + '" based at "' + directory + '":'

    col_width = 12      # Size of a display column
    col_spacing = 4     # Spacing b/w columns

    results = globx.globx(directory, pattern)
    for elem in results:
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
        print elem


# Entry point
if __name__ == '__main__':
    main()

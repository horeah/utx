#
# Equivalent of a friendlier, recursive version of rm
#
# Delete (recursively) files that match a given pattern
#
# Author: Horea Haitonic
#

import sys, globx, optparse, os
from sys import stdout, stderr, stdin


def main():
    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'rmx [options] <files>',
                                   version = '10.1')
    parser.add_option('-i', '--interactive', 
                      action = 'store_true', dest = 'interactive', 
                      default = False,
                      help = 'confirm deletion for each file')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # Interpret the <files> argument
    if len(args) == 0:
        stderr.write('You must specify the files to delete')
        sys.exit(1)
    else:
        (directory, pattern) = globx.split_target(args[0])

    if pattern.find('**'):
        options.interactive = True

    if options.verbose:
        print '>> Deleting "' + pattern + '" based at "' + directory + '":'

    results = globx.globx(directory, pattern)
    abort = False
    confirm_initial = None
    for elem in results:
        if options.interactive:
            confirm = confirm_initial
            while confirm == None :
                stdout.write('Delete "' + elem + '"? y/N/a(ll)/q(uit) ')
                read = stdin.readline()
                if len(read) == 1:
                    confirm = False
                elif len(read) == 2:
                    if read[0].upper() == 'Y':
                        confirm = True
                    elif read[0].upper() == 'N':
                        confirm = False
                    elif read[0].upper() == 'A':
                        confirm = True
                        confirm_initial = True
                    elif read[0].upper() == 'Q':
                        abort = True
                        break
            if abort:
                break
        else:
            confirm = True      # Confirmed by default in non-interactive

        if confirm:
            full_name = directory + '\\' + elem
            try:
                if os.path.isdir(full_name):
                    os.rmdir(full_name)
                else:
                    os.remove(full_name)
                if options.verbose:
                    stdout.write('>> Deleted "' + elem + '"\n')
            except OSError, e:
                stderr.write('  ' + e)


if __name__ == '__main__':
    main()

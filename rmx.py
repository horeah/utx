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
    parser.add_option('-i', '--interactive-cautious', 
                      action = 'store_true', dest = 'interactive_cautious', 
                      default = False,
                      help = 'cautiously (y/N) confirm deletion for each file')
    parser.add_option('-I', '--interactive-brave', 
                      action = 'store_true', dest = 'interactive_brave', 
                      default = False,
                      help = 'bravely (Y/n) confirm deletion for each file')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # Arguments sanity check
    if options.interactive_brave and options.interactive_cautious:
        parser.error("options -i and -I are mutually exclusive")

    # Interpret the <files> argument
    if len(args) == 0:
        parser.error('You must specify the files to delete')
    else:
        (directory, pattern) = globx.split_target(args[0])

    # Prepare the interactive mode (if specified)
    if pattern.find('**'):
        options.interactive_cautious = True
    if options.interactive_brave:
        default_input = 'Y'
    elif options.interactive_cautious:
        default_input = 'N'
    options.interactive = options.interactive_cautious or options.interactive_brave

    if options.verbose:
        print '>> Deleting "' + pattern + '" based at "' + directory + '":'

    results = globx.globx(directory, pattern)
    abort = False
    confirm_initial = None
    for elem in results:
        if options.interactive:
            confirm = confirm_initial
            while confirm == None :
                stdout.write('Delete "' + elem + '"? [')
                if options.interactive_brave:
                    stdout.write('Y/n')
                else:   # options.interactive_cautious
                    stdout.write('y/N')
                stdout.write('/a(ll)/q(uit)]: ')

                read = stdin.readline()
                if len(read) == 1:
                    confirm = options.interactive_brave
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

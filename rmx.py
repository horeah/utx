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
                      action = 'store', type = 'int', dest = 'interactive', 
                      default = None,
                      metavar = 'level',
                      help = 'interactively confirm deletion (level=0..3)')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # The files argument
    if len(args) == 0:
        parser.error('You must specify the files to delete')
    (directory, pattern) = globx.split_target(args[0])

    # The interactive level
    if options.interactive == None:
        if pattern.find('**') >= 0:
            options.interactive = 3
        else:
            options.interactive = 0
    if not options.interactive in range(0, 4):
        parser.error('The interactive level has to be in [0..3]')



    if options.verbose:
        print '>> Deleting "' + pattern + '" based at "' + directory + '":'

    results = globx.globx(directory, pattern)
    abort = False
    confirm_initial = None
    collected_results = []
    for elem in results:
        if options.interactive == 0:
            confirm = True
        elif options.interactive == 1:
            confirm = False
        else:    # options.interactive > 1
            confirm = confirm_initial
            while confirm == None :
                stdout.write('Delete "' + elem + '"? [')
                if options.interactive == 2:
                    stdout.write('Y/n')
                else:   # options.interactive == 3
                    stdout.write('y/N')
                stdout.write('/a(ll)/q(uit)]: ')

                read = stdin.readline()
                if len(read) == 1:
                    confirm = options.interactive == 2
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

        if confirm:
            # Confirmed for this file, execute deletion
            remove_file(directory, elem, options.verbose)
        elif options.interactive == 1:
            # In interactive == 1, just list the files and confirm at the end
            collected_results.append(elem)
            stdout.write(elem + '\n')
    

    if options.interactive == 1:
        # Confirmation at the end
        if len(collected_results) > 0:
            confirm = None
            while confirm == None :
                stdout.write('Delete ' + str(len(collected_results)) + ' files? [y/N]: ')
                read = stdin.readline()
                if len(read) == 1:
                    confirm = False
                elif len(read) == 2:
                    if read[0].upper() == 'Y':
                        confirm = True
                    elif read[0].upper() == 'N':
                        confirm = False

            if confirm:
                for elem in collected_results:
                    remove_file(directory, elem, options.verbose)
        else:
            stdout.write('No files to delete\n')

                
def remove_file(directory, name, verbose = False):
    """
    Try to delete a specified file or directory

    Report any error; report what's being done if the verbose flag is 
    True
    """
    full_name = directory + '\\' + name
    try:
        if os.path.isdir(full_name):
            os.rmdir(full_name)
        else:
            os.remove(full_name)
            if verbose:
                stdout.write('>> Deleted "' + name + '"\n')
    except OSError, e:
        stderr.write('  ' + str(e) + '\n')
    


if __name__ == '__main__':
    main()

#
# Equivalent of a friendlier, recursive version of rm
#
# Delete (recursively) files that match a given pattern
#
# Author: Horea Haitonic
#

import sys, globx, optparse, os, shutil
from sys import stdout, stderr
from actions import apply_confirm


def main():
    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'rmx [options] <files>',
                                   description = 
"""Delete (recursively) files and directories that match a given pattern.
You can use the well-known '*' and '?' as expected, '**' to recursively
match subdirectories and a '\\\\' (double backslash) to mark the base
directory.""",

                                   version = '0.1')
    parser.add_option('-i', '--interactive', 
                      action = 'store', type = 'int', dest = 'interactive', 
                      default = None,
                      metavar = 'level',
                      help = 'interactively confirm deletion (level=0..3)')
    parser.add_option('-r', '--recursive',
                      action = 'store_true', dest = 'recursive',
                      default = False,
                      help = 'also delete directories (default if ** is used)')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # The files argument
    if len(args) == 0:
        parser.error('You must specify the files to delete')
    (directory, pattern) = globx.split_target(args[0].replace('/', '\\'))
    if directory == '':
        directory = '.'


    # Automatically enable recursive mode if needed
    if globx.is_recursive(pattern):
        options.recursive = True
        if options.verbose:
            stdout.write('>> Auto enabled recursive copy due to a recursive glob\n')
    elif not globx.is_glob(pattern) and os.path.isdir(directory + '\\' + pattern):
        options.recursive = True
        if options.verbose:
            stdout.write('>> Auto enabled recursive deletion since the target is a directory\n')

    # The interactive level
    if options.interactive == None:
        if options.recursive:
            options.interactive = 3
        else:
            options.interactive = 0
    if not options.interactive in range(0, 4):
        parser.error('The interactive level has to be in [0..3]')

    if options.verbose:
        print '>> Deleting "' + pattern + '" based at "' + directory + '":'

    results = globx.globx(directory, pattern)
    apply_confirm(results,
                  'delete',
                  lambda elem: remove_file(directory, 
                                           elem,
                                           options.verbose,
                                           options.recursive),
                  options.interactive)

                
def remove_file(directory, name, verbose = False, recursive = False):
    """
    Try to delete a specified file or directory

    Report any error; report what's being done if the verbose flag is 
    True
    """
    full_name = directory + '\\' + name
    try:
        if os.path.isdir(full_name):
            if recursive:
                shutil.rmtree(full_name)
            else:
                stdout.write('>> Omitting directory "' + full_name + '"\n')
                return
        else:
            os.remove(full_name)
        if verbose:
            stdout.write('>> Deleted "' + name + '"\n')
    except OSError, e:
        stderr.write('  ' + str(e) + '\n')
    


if __name__ == '__main__':
    main()

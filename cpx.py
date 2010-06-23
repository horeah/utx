#
# Equivalent of a friendlier, recursive version of cp
#
# Copy files that match a given (possibly recursive) pattern
#
# Author: Horea Haitonic
#

import sys, globx, optparse, os, shutil
from sys import stdout, stderr, stdin


def main():
    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'cpx [options] <files> <destination>',
                                   description = 
"""Copy (recursively) files and directories that match a given pattern.
You can use the well-known '*' and '?' as expected, '**' to recursively
match subdirectories and a '\\\\' (double backslash) to mark the base
directory.""",

                                   version = '0.1')
    parser.add_option('-i', '--interactive', 
                      action = 'store', type = 'int', dest = 'interactive', 
                      default = 0,
                      metavar = 'level',
                      help = 'interactively confirm operations (level=0..3)')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # The files argument
    if len(args) <= 1:
        parser.error('You must specify both the source and the destination')
    (directory, pattern) = globx.split_target(args[0])
    destination = args[1]
    if not os.path.isdir(destination):
        stderr.write(sys.argv[0] + ': error: the <destination> has to be an existing directory\n')
        sys.exit(1)

    # The interactive level
    if not options.interactive in range(0, 4):
        parser.error('The interactive level has to be in [0..3]')

    if options.verbose:
        print '>> Copying "' + pattern + '" based at "' + directory + '"'
        print '>>      To "' + destination + '"'

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
                stdout.write('Copy "' + elem + '"? [')
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
            copy_file(directory, elem, destination, options.verbose)
        elif options.interactive == 1:
            # In interactive == 1, just list the files and confirm at the end
            collected_results.append(elem)
            stdout.write(elem + '\n')
    

    if options.interactive == 1:
        # Confirmation at the end
        if len(collected_results) > 0:
            confirm = None
            while confirm == None :
                stdout.write('Copy ' + str(len(collected_results)) + ' files? [y/N]: ')
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
                    copy_file(directory, elem, destination, options.verbose)
        else:
            stdout.write('No files to copy\n')

                
def copy_file(directory, name, destination, verbose = False):
    """
    Try to copy a specified file or directory

    Report any error; report what's being done if the verbose flag is 
    True
    """
    full_name = directory + '\\' + name
    target_full_name = destination + '\\' + name
    try:
        (target_path, target_base) = os.path.split(target_full_name)
        if not os.path.isdir(target_path):
            os.makedirs(target_path)
        if os.path.isdir(full_name):
            shutil.copytree(full_name, target_full_name)
        else:
            shutil.copyfile(full_name, target_full_name)
        if verbose:
            stdout.write('>> Copied "' + name + '"\n')
    except OSError, e:
        stderr.write('  ' + str(e) + '\n')
    


if __name__ == '__main__':
    main()

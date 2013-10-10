#
# Equivalent of a friendlier, recursive version of cp
#
# Copy files that match a given (possibly recursive) pattern
#
# Author: Horea Haitonic
#

import sys, globx, optparse, os, shutil, itertools, signal, threading
import util, console
from sys import stdout, stderr, stdin
from actions import ConfirmedAction

def main():
    # Prevent stacktraces on Ctrl-C
    signal.signal(signal.SIGINT, util.exit_on_ctrl_c)

    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'cpx [options] <files> <destination>',
                                   description = 
"""Copy (recursively) files and directories that match a given pattern.
You can use the well-known '*' and '?' as expected, '**' to recursively
match subdirectories and a '\\\\' (double backslash) to mark the base
directory.""",
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
    parser.add_option('-i', '--interactive', 
                      action = 'store', type = 'int', dest = 'interactive', 
                      default = 0,
                      metavar = 'level',
                      help = 'interactively confirm operations (level=0..3)')
    parser.add_option('-r', '--recursive',
                      action = 'store_true', dest = 'recursive',
                      default = False,
                      help = 'also copy directories (default if ** is used)')
    parser.add_option('-c', '--create',
                      action = 'store_true', dest = 'create_destination',
                      default = False,
                      help = 'create destination directory if missing')
    parser.add_option('-v', '--verbose',
                      action = 'store_true', dest = 'verbose',
                      default = False,
                      help = 'describe the operations being performed')
    (options, args) = parser.parse_args()

    # The interactive level
    if not options.interactive in range(0, 4):
        parser.error('The interactive level has to be in [0..3]')

    # The source argument
    if len(args) <= 1:
        parser.error('You must specify both the source and the destination')

    # The destination argument
    destination = args[-1].replace('/', '\\')
    if not os.path.isdir(destination):
        if options.interactive > 0:
            confirm = None
        else:
            confirm = options.create_destination

        while confirm == None:
            stdout.write('>> Destination "' 
                         + destination 
                         + '" missing. Create? [Y/n]')
            read = stdin.readline()
            if len(read) == 1:
                confirm = True
            elif len(read) == 2:
                if read[0].upper() == 'Y':
                    confirm = True
                elif read[0].upper() == 'N':
                    confirm = False
        if confirm:
            # Confirmed, create directory
            try:
                os.mkdir(destination);
            except OSError, e:
                stderr.write('  ' + str(e) + '\n')
                sys.exit(3)
        else:
            stderr.write(sys.argv[0] + ': error: the <destination> has to be an existing directory\n')
            sys.exit(1)

    for arg in args[:-1]:
        (directory, pattern) = globx.split_target(arg.replace('/', '\\'))
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
                stdout.write('>> Auto enabled recursive copy since the source is a directory\n')


        if options.verbose:
            print '>> Copying "' + pattern + '" based at "' + directory + '"'
            print '>>      To "' + destination + '"'

        # Expand pattern and filter 
        results = globx.globx(directory, pattern)
        filtered_results = itertools.ifilter(
            lambda x: 
            [e for e in options.exclude_list if globx.matches_path(x, e)] == [] and \
            [e for e in options.exclude_list_ending if globx.matches_path(x, e, True)] == [],
            results)

        # Create the copy action and run it
        copy_action = ConfirmedCopy()
        copy_action.directory = directory
        copy_action.destination = destination
        copy_action.verbose = options.verbose
        copy_action.recursive = options.recursive
        copy_action.interactive = options.interactive
        copy_action.apply_confirm(filtered_results)


class ConfirmedCopy(ConfirmedAction):
    """
    Implements a confirmed file copy action based on the ConfirmedAction
    classs
    """
    directory = '.'

    destination = '.'

    verbose = False

    recursive = False

    def ask_one(self, name):
        if (os.path.isdir(self.directory + '\\' + name)):
            name += '\\'
        return 'Copy "' + name + '"?'

    def ask_all(self, items):
        return 'Copy ' + str(len(items)) + ' files?'

    def no_items(self):
        return 'No files to copy'

    def action(self, name):
        self._copy(self.directory, name, self.destination, self.verbose, self.recursive)

    def _copy(self, directory, name, destination, verbose, recursive):
        """Utility function that recursively copies files and directories"""
        already_copied = []
        full_name = directory + '\\' + name
        target_full_name = destination + '\\' + name
        try:
            (target_path, target_base) = os.path.split(target_full_name)
            if not os.path.isdir(target_path):
                os.makedirs(target_path)

            if os.path.isdir(full_name):
                if recursive:
                    for f in os.listdir(full_name):
                        self._copy(full_name, f, target_full_name, False, True)
                else:
                    return
            else:
                # We avoid copying the same file repeatedly -- this can happen
                # when copying **\* due to directories matching both the ** and
                # the *.
                if not full_name in already_copied:
                    source_size = float(os.path.getsize(full_name))
                    worker = threading.Thread(group=None,
                                              target = shutil.copyfile,
                                              name='copy-file',
                                              args = (full_name, target_full_name))
                    worker.setDaemon(True)  # So that we can exit on Ctrl-C
                    worker.start()
                    while worker.isAlive():
                        if verbose and stdout.isatty() and os.path.exists(target_full_name):
                            destination_size = os.path.getsize(target_full_name)
                            if destination_size > 0:
                                percent = 100 * destination_size / source_size
                            else:
                                # Special treatment for zero-sized files
                                percent = 100
                            if percent < 100:
                                stdout.write('%8.2f%% "%s"' % (percent, name))
                                console.cursor_backward(12 + len(name))
                        worker.join(0.2)
                    if verbose:
                        stdout.write('>> Copied "' + name + '"\n')
                    already_copied.append(full_name)

        except OSError, e:
            stderr.write('  ' + str(e) + '\n')
        except IOError, e:
            stderr.write('  ' + str(e) + '\n')

if __name__ == '__main__':
    main()

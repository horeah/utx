#
# Equivalent of a friendlier, recursive version of cp
#
# Copy files that match a given (possibly recursive) pattern
#
# Author: Horea Haitonic
#

import sys, optparse, os, shutil, itertools, signal, threading, win32file
import globx, util, console
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
                                   version = '0.3.1')
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
    parser.add_option('-m', '--require-match', choices = ('1', '0'),
                      metavar = 'MATCH_REQUIRED',
                      help = 'require (1) or not (0) at least one file/dir to match')
    parser.add_option('-u', '--update',
                      action = 'store_true', dest = 'update',
                      default = False,
                      help = 'copy only when destination is older or missing')
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

    # We accept both '/' and '\\' in exclusion lists
    options.exclude_list = [e.replace('/', '\\') for e in options.exclude_list]
    options.exclude_list_ending = [e.replace('/', '\\') for e in options.exclude_list_ending]

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
            pattern += '\\**\\*'
            if options.verbose:
                stdout.write('>> Auto enabled recursive copy since the source is a directory\n')

        if options.require_match is None and not globx.is_glob(pattern):
            options.require_match = '1'

        if options.verbose:
            print '>> Copying "' + pattern + '" based at "' + directory + '"'
            print '>>      To "' + destination + '"'

        if options.require_match is '1':
            check_any = globx.globx(directory, pattern)
            try:
                check_any.next()
            except StopIteration, _:
                sys.stderr.write('%s: error: "%s" did not match any file or directory\n'
                                 % (sys.argv[0], pattern))
                sys.exit(1)

        results = globx.globx(directory, pattern)
        filtered_results = itertools.ifilter(
            lambda x:
            [e for e in options.exclude_list if globx.matches_path(x, e)] == [] and \
            [e for e in options.exclude_list_ending if globx.matches_path(x, e, True)] == [],
            results)
        if options.recursive:
            # for recursive copying we need to exclude directory names
            filtered_results = itertools.ifilter(
                lambda x: not os.path.isdir(os.path.join(directory, x)),
                filtered_results)

        # Create the copy action and run it
        copy_action = ConfirmedCopy()
        copy_action.directory = directory
        copy_action.destination = destination
        copy_action.verbose = options.verbose
        copy_action.recursive = options.recursive
        copy_action.interactive = options.interactive
        copy_action.update = options.update
        try:
            copy_action.apply_confirm(filtered_results)
        except Exception, e:
            stderr.write('  ' + str(e) + '\n')
            sys.exit(1)


class ConfirmedCopy(ConfirmedAction):
    """
    Implements a confirmed file copy action based on the ConfirmedAction
    classs
    """
    directory = '.'

    destination = '.'

    verbose = False

    recursive = False

    update = False

    def ask_one(self, name):
        if (os.path.isdir(self.directory + '\\' + name)):
            name += '\\'
        return 'Copy "' + name + '"?'

    def ask_all(self, items):
        return 'Copy ' + str(len(items)) + ' files?'

    def no_items(self):
        return 'No files to copy'

    def action(self, name):
        self._copy(self.directory, name, self.destination, self.verbose, self.recursive, self.update)

    def _copy(self, directory, name, destination, verbose, recursive, update):
        """Utility function that recursively copies files and directories"""
        already_copied = []
        full_name = directory + '\\' + name
        target_full_name = destination + '\\' + name
        (target_path, target_base) = os.path.split(target_full_name)
        if not os.path.isdir(target_path):
            os.makedirs(target_path)

        if os.path.isdir(full_name):
            if recursive:
                for f in os.listdir(full_name):
                    self._copy(full_name, f, target_full_name, verbose, True, update)
            else:
                return
        else:
            # We avoid copying the same file repeatedly -- this can happen
            # when copying **\* due to directories matching both the ** and
            # the *.
            if not full_name in already_copied:
                if update and os.path.isfile(target_full_name):
                    if os.path.getmtime(target_full_name) >= os.path.getmtime(full_name):
                        # Destination is newer than source, skip this file
                        if verbose:
                            stdout.write('>> Skipped "' + name + '"\n')
                        return

                source_size = float(os.path.getsize(full_name))
                self._failure = None
                def copyfile_wrapper(full_name, target_full_name):
                    try:
                        win32file.CopyFile(full_name, target_full_name, False)
                    except Exception, e:
                        self._failure = e

                worker = threading.Thread(group=None,
                                          target = copyfile_wrapper,
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

                if self._failure:  # Propagate exception from thread
                    raise self._failure
                if verbose:
                    stdout.write('>> Copied "' + name + '"\n')
                already_copied.append(full_name)                    


if __name__ == '__main__':
    main()

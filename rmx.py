#
# Equivalent of a friendlier, recursive version of rm
#
# Delete (recursively) files that match a given pattern
#
# Author: Horea Haitonic
#

import sys, globx, util, optparse, os, shutil, itertools, signal
from sys import stdout, stderr
from actions import ConfirmedAction


def main():
    # Prevent stacktraces on Ctrl-C
    signal.signal(signal.SIGINT, util.exit_on_ctrl_c)

    # Define and parse command line otions 
    parser = optparse.OptionParser(usage = 'rmx [options] <files>',
                                   description = 
"""Delete (recursively) files and directories that match a given pattern.
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
    filtered_results = itertools.ifilter(
        lambda x: 
        [e for e in options.exclude_list if globx.matches_path(x, e)] == [] and \
        [e for e in options.exclude_list_ending if globx.matches_path(x, e, True)] == [],
        results)

    remove_action = ConfirmedRemove()
    remove_action.directory = directory
    remove_action.verbose = options.verbose
    remove_action.interactive = options.interactive
    remove_action.recursive = options.recursive
    remove_action.apply_confirm(filtered_results)


class ConfirmedRemove(ConfirmedAction):
    """
    Implements a confirmed file-deletion based on the ConfirmedAction
    class.
    """
    directory = '.'

    def ask_one(self, name):
        if (os.path.isdir(self.directory + '\\' + name)):
            name += '\\'
        return 'Delete "' + name + '"?'

    def ask_all(self, items):
        return 'Delete "' + str(len(items)) + '?'

    def no_items(self):
        return 'No items to delete'

    def action(self, name):
        full_name = self.directory + '\\' + name
        try:
            if os.path.isdir(full_name):
                if self.recursive:
                    shutil.rmtree(full_name)
                else:
                    stdout.write('   Omitting directory "' + full_name + '"\n')
                    return
            else:
                os.remove(full_name)
            if self.verbose:
                stdout.write('   Deleted "' + name + '"\n')
        except OSError, e:
            stderr.write('  ' + str(e) + '\n')
                    

if __name__ == '__main__':
    main()

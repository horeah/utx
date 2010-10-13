from sys import stdout, stdin


class ConfirmedAction(object):
    """
    Complex action that can be applied after user confirmation
    """

    # Interactivity level
    interactive = 0

    def ask_one(self, name):
        """The question to ask for individual confirmation"""
        return 'Perform on "' + name + '"?'

        
    def ask_all(self, items):
        """The question to ask for multiple confirmation"""
        return 'Perform on ' + str(len(items)) + ' items?'
        

    def no_items(self):
        """The message to print when no items have been confirmed"""
        return 'No items to process'


    def action(self, name):
        """The actual action that is to be applied for each item"""
        stdout.write('Processing "' + name + '"\n')


    def apply_confirm(self, items):
        """Apply the custom action on a set of items, confirming as needed"""
        abort = False
        confirm_initial = None
        collected_items = []
        for elem in items:
            if self.interactive == 0:
                confirm = True
            elif self.interactive == 1:
                confirm = False
            else:    # interactive > 1
                confirm = confirm_initial
                while confirm == None :
                    stdout.write(self.ask_one(elem))
                    stdout.write(' [')
                    if self.interactive == 2:
                        stdout.write('Y/n')
                    else:   # interactive == 3
                        stdout.write('y/N')
                    stdout.write('/a(ll)/q(uit)]: ')

                    read = stdin.readline()
                    if len(read) == 1:
                        confirm = self.interactive == 2
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
                # Confirmed for this file, apply action
                self.action(elem)
            elif self.interactive == 1:
                # In interactive == 1, just list the files and confirm at the end
                collected_items.append(elem)
                stdout.write(elem + '\n')


        if self.interactive == 1:
            # Confirmation at the end
            if len(collected_items) > 0:
                confirm = None
                while confirm == None :
                    stdout.write(self.ask_all(collected_items))
                    stdout.write(' [y/N]: ')
                    read = stdin.readline()
                    if len(read) == 1:
                        confirm = False
                    elif len(read) == 2:
                        if read[0].upper() == 'Y':
                            confirm = True
                        elif read[0].upper() == 'N':
                            confirm = False

                if confirm:
                    for elem in collected_items:
                        self.action(elem)
            else:
                stdout.write(self.no_items())

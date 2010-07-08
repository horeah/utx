from sys import stdout, stdin

def apply_confirm(items, action_name, action, interactive):
    """
    Confirm and apply a given action to the specified items
    
    - items contains the target elemens (on which the action is to be applied)
    - action_name is used when displaying confirmation messages
    - action is a function with one argument, defining the actual action to
      apply for each element
    - interactive is the interactivity level (0..3)

    """
    abort = False
    confirm_initial = None
    collected_items = []
    for elem in items:
        if interactive == 0:
            confirm = True
        elif interactive == 1:
            confirm = False
        else:    # interactive > 1
            confirm = confirm_initial
            while confirm == None :
                stdout.write(action_name.capitalize() + ' "' + elem + '"? [')
                if interactive == 2:
                    stdout.write('Y/n')
                else:   # interactive == 3
                    stdout.write('y/N')
                stdout.write('/a(ll)/q(uit)]: ')

                read = stdin.readline()
                if len(read) == 1:
                    confirm = interactive == 2
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
            action(elem)
        elif interactive == 1:
            # In interactive == 1, just list the files and confirm at the end
            collected_items.append(elem)
            stdout.write(elem + '\n')
    

    if interactive == 1:
        # Confirmation at the end
        if len(collected_items) > 0:
            confirm = None
            while confirm == None :
                stdout.write(action_name.capitalize() + ' ' 
                             + str(len(collected_items)) 
                             + ' files? [y/N]: ')
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
                    action(elem)
        else:
            stdout.write('No files to ' + action_name + '\n')

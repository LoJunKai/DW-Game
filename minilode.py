import re
import cmd
import copy
import random
import numpy as np
from libdw import sm

try:
    from pyreadline import Readline
except:
    print(
        "Readline module part of the python standard library, but it does not work in windows. "
        "Hence, to enable TAB completion features, run the command:\n"
        "pip install pyreadline")

'''
# TODO
# Game mechanic: Anyway to add spaces after do_dig, so that it will be dig .
# Game mechanic: Set boundary of travallable area to exclude the first row (so that H won't get eaten up)
# Game mechanic: Show what has been excavated so that users would know
# Intro message: type <help or ?> followed by <command> to get more info on the command
# Intro message: when an empty line is entered, the previous input would be run. So becareful on that!
# Intro message: use up down keys to cycle through command history
# Intro message: press <tab> to auto complete input or to show list of commands available
# State machine: implement nested interpreters when changing from different states
'''

class App(cmd.Cmd, sm.SM):
    start_state = "Intro"

    def __init__(self):
        print("\n__Start message here__")
        super(App, self).__init__()

    def intro(self):
        # Introductory message
        print("Once upon a time.....")
        print("\n__Welcome to Minilode__")
        ans = input("press <enter> to continue: ")

        if ans == 'skip':
            changes = self.step("Home")
            home = Home(changes)
            home.cmdloop()

        else:
            self.step("Tutorial")

    def do_play(self, argv):
        self.step("Play")

    def do_tutorial(self, argv):
        self.step("Intro")

    def get_next_values(self, state, inp):
        if state == "Intro":
            if inp == "Home":
                changes = "I changed these settings".split(" ")

                return ("Home", changes)
                
            elif state == "Tutorial":
                    super(App, self).__init__()
                    self.intro = "Beginning Tutorial"
                    self.prompt = "(Tutorial) "



        # state == "Home":
        #   if inp == "Play":
        #       game = Game()
        #       game.prompt = "(Minilode) "
        #       game.cmdloop()
        #       return ("Play", None)
        #   elif inp == "Intro":
        #       print("Intro message")
        

# Trying to override the functions available is not working. Harder than expected
# Can try partial inheritance - 
# Or maybe just scrape the whole idea and just do simple input - only game then use cmd.Cmd()

class Home(App):
    def __init__(self, changes):
        super(Home, self).__init__()
        self.intro = "You are at home"
        self.prompt = "(Home) "
        self.changes = changes

    def do_play(self, argv):
        game = Game()
        game.prompt = "(Minilode) "
        game.cmdloop()

    def do_help(self, argv):
        cmds_doc = self.changes
        super(Home, self).do_help(argv)
        self.print_topics(self.doc_header, cmds_doc, 15, 80, custom=True)

    def print_topics(self, header, cmds, cmdlen, maxcol, custom=False):
        """ 
        This is to overide cmd.Cmd method of printing help statement,
        So that my custom message could be printed
        """
        if header == "Documented commands (type help <topic>):" and not custom:
            # Override implemented command
            return
        else:
            super(Home, self).print_topics(header, cmds, cmdlen, maxcol)

    def completenames(self, text, *ignored):
        return self.changes


class Game(App):
    mmap = ""
    _available_directions = ["left", "right", "up", "down"]
    _coins_type = {' ': 0, '#': -1, 'G': 25}
    position = [1, 1]
    points = 0

    def __init__(self):
        super(App, self).__init__()
        self.intro = "__Intro message here__"
        self.create_map()

    def create_map(self):
        size = 15  # 15*15 digging ground
        mmap = np.ndarray((size, size), dtype='<U1')
        mmap[:2, :] = ' '  # First 2 rows are for ground level
        mmap[2:, :] = '#'  # Rest are digging ground
        mmap[0, :4] = 'H'  # home
        mmap[1, 1] = 'M'  # Minilode
        self.position = [1, 1]
        self.coins = 30  # Starting points

        # Gold
        for i in range(10):
            row = random.randint(2, size-1)
            col = random.randint(0, size-1)
            mmap[row, col] = 'G'  # Gold

            # TODO
            # Get a random int --> number of gunk
            # random choices of 5*5 area matrix for i for j in range(-2,3) a.append((i,j)) --> relative position of gunk
            # These values + row/col values to get the final position of gunk

        self.mmap = mmap

    def display_map(self):
        print(f"Cash: ${self.coins}")
        for row in self.mmap:
            print('\t', end=' ')
            for col in row:
                print(str(col), end=' ')
            print('')


    def do_dig(self, direction_steps):
        ''' Get the points in the path '''

        # Parse input
        lst = direction_steps.split(' ')  # "dig" --> [''], "dig <word>" --> ['<word>']
        if lst[0] not in self._available_directions:
            print("*** commands should be either {}".format(', '.join(self._available_directions)))
            return

        if len(lst) == 1:
            # if steps is not provided, it defaults to 1  
            lst.append(1)
        elif len(lst) > 2:
            print("*** Unknown syntax:", direction_steps)
            print("Type 'help dig' for more info")
            return

        direction, steps = lst
        try:
            steps = int(steps)
        except:
            print("*** You need to type in an integer after the direction")
            return

        # Run dig function to move and add coins
        self.dig(direction, steps)
        return

    def dig(self, direction, steps):
        ''' Gains coins '''

        row, col = self.position

        # Adjust minilode's position
        if direction == 'left':
            self.position[1] -= steps  # Change position
            path = copy.deepcopy(self.mmap[row, self.position[1]:col])  # Get what's in between
            self.mmap[row, self.position[1]:col] = ' '  # Erase what's in between

        elif direction == "right":
            self.position[1] += steps
            path = copy.deepcopy(self.mmap[row, col+1:self.position[1]+1])  # needs to add 1 to exclude it's current location
            self.mmap[row, col+1:self.position[1]+1] = ' '

        elif direction == "up":
            self.position[0] -= steps
            path = copy.deepcopy(self.mmap[self.position[0]:row, col])
            self.mmap[self.position[0]:row, col] = ' '

        elif direction == "down":
            self.position[0] += steps
            path = copy.deepcopy(self.mmap[row+1:self.position[0]+1, col])
            self.mmap[row+1:self.position[0]+1, col] = ' '
        
        # Add coins
        self.addcoins(path)

        # Update the position marking
        self.mmap[row, col] = ' '
        row, col = self.position
        self.mmap[row, col] = 'M'

        # Display map
        self.display_map()

    def addcoins(self, path):
        for i in path:
            self.coins += self._coins_type[i]


    def complete_dig(self, text, line, begidx, endidx):
        # text is the string we are matching against, all returned matches must begin with it
        # line is is the current input line
        # begidx is the beginning index in the line of the text being matched
        # endidx is the end index in the line of the text being matched

        return [i+' ' for i in self._available_directions if i.startswith(text)]

    def help_dig(self):
        arr = "-->"
        print("\t{: <13} {: <7} dig <direction> <steps>".format("format", arr))
        print("\t{: <13} {: <7} {}".format("direction", arr, ', '.join(self._available_directions)))
        print("\t{: <13} {: <7} needs to be an integer.".format("steps", arr))

app = App()
app.start()
app.intro()
# App().step(inp)
# App().cmdloop()

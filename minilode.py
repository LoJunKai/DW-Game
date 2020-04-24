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
# Major Error: Currently once do_set_checkpoints is deleted, cannot be set back
# Tutorial:
I thought of a short cut to make my tutorial super easy to implement
Since I already have help functions, I shall just ask them to use the help functions
Then I just write a bit on the game mechanics and shortcut
Then provide them with unlimited health as a sandbox for them

# Game mechanic: Anyway to add spaces after do_dig, so that it will be dig .
# Game mechanic: Show what has been excavated so that users would know
# Intro message: type <help or ?> followed by <command> to get more info on the command
# Intro message: when an empty line is entered, the previous input would be run. So becareful on that!
# Intro message: use up down keys to cycle through command history
# Intro message: press <tab> to auto complete input or to show list of commands available
# if you want: When you lose, print the mmap of the losing position
'''

class App(cmd.Cmd, sm.SM):
    start_state = "Intro"

    def __init__(self):
        print("\n__Start message here__")
        super(App, self).__init__()
        self.start()

        # Introductory message
        print("Once upon a time.....")
        print("\n__Welcome to Minilode__")
        ans = input("press <enter> to continue: ")

        if ans == 'skip':
            return self.step("Home")()
        else:
            return self.step("Tutorial")()

    def ask(self, commands):
        ans = []
        while ans not in commands:
            ans = input(" ".join(commands)+'\n').capitalize()
        return ans

    def home(self):
        print('__MINILODE LOGO__')
        print("Where would you like to go?")
        commands = ["Play", "Tutorial"]
        ans = self.ask(commands)
        return self.step(ans)()

    def tutorial(self):
        print("Welcome to the tutorial")
        game = Game()  # TODO: change this to the tutorial version
        game.intro = "Let's go!"
        game.prompt = "(Tutorial) "
        game.cmdloop()

        # Return to Home
        return self.step("Home")()

    def play(self):
        game = Game()
        game.intro = "Starting Game..."
        game.prompt = "(Minilode) "
        game.cmdloop()

        # Return to home
        return self.step("Home")()

    def get_next_values(self, state, inp):
        # This State Machines is totally useless, go find a way to better use it!!
        # Customise the print statements or something
        print('')
        if inp == "Home":
            return ("Home", self.home)

        if state == "Intro":
            if inp == "Tutorial":
                return ("Home", self.tutorial)

        if state == "Home":
            if inp == "Play":
                print("PLAYYYYYY")
                return ("Home", self.play)

            elif inp == "Tutorial":
                return ("Home", self.tutorial)


class Game(cmd.Cmd, sm.SM):
    mmap = ""
    _available_directions = ["left", "right", "up", "down"]
    _coins_type = {'J': -5, '#': -1, 'G': 25}
    _coins_text = {'J': "Junk", '#': "Dirt", 'G': "Gold"}
    _size = 15  # 15*15 digging ground
    _position = [1, 1]
    _items_price = {"Checkpoints": 5, "Sonar": 25}
    _items_inventory = {"Checkpoints": 0, "Sonar": 0}
    _checkpoints = {}
    coins = 0

    def __init__(self):
        super(Game, self).__init__()
        self.intro = "__Intro message here__"
        self.create_map()
        # self.checkpoints()  # Hide the checkpoints related fn first

    def create_map(self):
        mmap = np.ndarray((self._size, self._size), dtype='<U1')
        mmap[:2, :] = ' '  # First 2 rows are for ground level
        mmap[2:, :] = '#'  # Rest are digging ground
        mmap[0, :4] = 'H'  # home
        mmap[1, 1] = 'M'  # Minilode
        self._position = [1, 1]
        self.coins = 30  # Starting coins

        # Gold
        for i in range(10):
            g_row = random.randint(2, self._size-1)
            g_col = random.randint(0, self._size-1)
            mmap[g_row, g_col] = 'G'  # Gold

            # TODO
            # Get a random int --> number of gunk
            # random choices of 5*5 area matrix for i for j in range(-2,3) a.append((i,j)) --> relative position of gunk
            # These values + row/col values to get the final position of gunk
            rel = []
            junk = random.randint(1, 5)

            for i in range(junk):
                j_row = g_row + random.randint(-2,3)
                j_col = g_col + random.randint(-2,3)
                if j_row >= self._size or j_col >= self._size or j_row < 2 or j_col < 0:
                    # Out of game area
                    continue
                mmap[j_row, j_col] = 'J'  # Junk

        self.mmap = mmap
        self.display_map()

    def display_map(self):
        print(f"Cash: ${self.coins}")
        dmap = copy.deepcopy(self.mmap)
        for key, value in self._checkpoints.items():
            print(key, value)
            if dmap[value[0], value[1]] != 'M':
                dmap[value[0], value[1]] = str(key)

        print(dmap)
        print(self.mmap)
        for row in dmap:
            print('\t', end=' ')
            for col in row:
                # Cover up the special stones
                # if col in self._coins_type:
                #     col = '#'

                print(str(col), end=' ')
            print('')

    def do_store(self, argv):
        ''' Access the store '''
        if self._position[0] != 1 or self._position[1] > 3:
            print("Access denied!\nYou need to go back to <-- Home --> to access the store.")
            return 
        print("__Welcome to the store!__")
        print("You currently have:")
        print(f"Cash: ${self.coins}")
        for key, value in self._items_inventory.items():
            print(f"{key}: {value}", end='  ')
        print("\n\nYou have enough money for:")

        items_buy = []
        for key, value in self._items_price.items():
            if self.coins > value:
                items_buy.append(key)
                print(f"{key}: ${value}", end='  ')

        purchase = input("\n\nWhat would you like to buy?\n").capitalize()
        if purchase in items_buy:
            self.coins -= self._items_price[purchase]
            self._items_inventory[purchase] += 1

            if purchase == "Checkpoints":
                print("\nCongratulations, you just bought a checkpoint!")
                self.checkpoints()
            elif purchase == "Sonar":
                print("\nCongratulations, you just upgraded your Sonar!")
                self.sonar()
            print(f"{purchase}: {self._items_inventory[purchase]}")
            print(f"You are now left with ${self.coins}")

    def checkpoints(self):
        # Enable or disable do_set_checkpoints method
        print(self._items_inventory["Checkpoints"])
        if self._items_inventory["Checkpoints"]:
            setattr(self, "do_set_checkpoints", self.do_set_checkpoints)
        else:
            # No more checkpoints left
            print('deletinggg', getattr(self, 'do_set_checkpoints'))
            delattr(type(self), "do_set_checkpoints")

    def do_set_checkpoints(self, argv):
        ''' Set this spot as a checkpoint '''
        self._items_inventory["Checkpoints"] -= 1
        self._checkpoints[len(self._checkpoints)+1] = copy.deepcopy(self._position)
        self.checkpoints()

# TODOTODOTODOTODOTODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO 

    def do_teleport(self, argv):
        ''' Teleport minilode to this spot '''
        pass

    def sonar(self):
        # Reveal a self._items_inventory["Sonar"] tile around the robot
        pass

    def get_next_values(self, state, inp):
        # if sonar is 1, then self.items_price, sonar shall be 75 next
        if state == "store":
            pass

        elif state == "Outside":
            pass

    def do_dig(self, direction_steps):
        ''' Get the coins in the path '''

        # Parse input
        lst = direction_steps.split(' ')  # "dig" --> [''], "dig <word>" --> ['<word>']
        if lst[0] not in self._available_directions:
            print("*** commands should be either {}".format(', '.join(self._available_directions)))
            return

        # Remove consecutive spaces
        lst = [i for i in lst if i != '']

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
        return self.dig(direction, steps)

    def dig(self, direction, steps):
        ''' Gains coins '''

        row, col = self._position

        # Adjust minilode's position
        if direction == 'left':
            self.move([0, -1*steps])  # Change position
            path = copy.deepcopy(self.mmap[row, self._position[1]:col])  # Get what's in between
            self.mmap[row, self._position[1]:col] = ' '  # Erase what's in between

        elif direction == "right":
            self.move([0, steps])
            path = copy.deepcopy(self.mmap[row, col+1:self._position[1]+1])  # needs to add 1 to exclude it's current location
            self.mmap[row, col+1:self._position[1]+1] = ' '

        elif direction == "up":
            self.move([-1*steps, 0])
            path = copy.deepcopy(self.mmap[self._position[0]:row, col])
            self.mmap[self._position[0]:row, col] = ' '

        elif direction == "down":
            self.move([steps, 0])
            path = copy.deepcopy(self.mmap[row+1:self._position[0]+1, col])
            self.mmap[row+1:self._position[0]+1, col] = ' '
        
        # Add coins
        end = self.addcoins(path)

        if end:
            return end

        # Update the position marking
        self.mmap[row, col] = ' '
        row, col = self._position
        self.mmap[row, col] = 'M'

        # Display map
        self.display_map()

    def move(self, steps):
        # Game area is essentially _size*_size, minus the first row for HHHH markers
        for i in range(2):
            self._position[i] += steps[i]

            if self._position[i] < 1-i:  # First row is skipped
                self._position[i] = 1-i

            elif self._position[i] >= self._size:
                self._position[i] = self._size-1

    def addcoins(self, path):
        items = {i:0 for i in self._coins_type}
        for i in path:
            if i == ' ':
                continue
            self.coins += self._coins_type[i]
            items[i] += 1

            if self.coins < 0:
                print("Oh noes, you went out of coins...")
                print("You lose :(\n")
                return self.do_quit("Lose liaos")

        print("Items found:  ", end='')
        for key, value in items.items():
            print(f"{self._coins_text[key]}: {value}", end="  ")

        print('')

    def do_quit(self, argv):
        print("__Game Stats__")
        print("~~ Thanks for playing ~~")
        print("Bye! :>")
        return 1

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
# App().step(inp)
# App().cmdloop()

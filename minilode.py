import cmd
import copy
import random
import numpy as np
from libdw import sm


try:
    from pyreadline import Readline
except ImportError:
    print(
        "Readline module part of the python standard library, but it does not work in windows. "
        "Hence, to enable TAB completion features, run the command:\n"
        "pip install pyreadline")


class App(cmd.Cmd, sm.SM):
    ''' Main app '''
    start_state = "Intro"
    minilode_logo = """
                     ___  ___   __   __   __   __   __        ______    _______   _______ 
                    |   \/   | |  | |  \ |  | |  | |  |      /  __  \  |       \ |   ____|
                    |  \  /  | |  | |   \|  | |  | |  |     |  |  |  | |  .--.  ||  |__   
                    |  |\/|  | |  | |  . `  | |  | |  |     |  |  |  | |  |  |  ||   __|  
                    |  |  |  | |  | |  |\   | |  | |  `----.|  `--'  | |  '--'  ||  |____ 
                    |__|  |__| |__| |__| \__| |__| |_______| \______/  |_______/ |_______|

                    """

    def __init__(self):
        print("Game initialising...")
        super(App, self).__init__()
        self.start()
        ans = self.step("Intro")
        return self.step(ans)()

    def ask(self, commands):
        ans = []
        while ans not in commands:
            ans = input(" ".join(commands) + '\n').capitalize()
        return ans

    def home(self):
        print(self.minilode_logo)
        print("Where would you like to go?")
        commands = ["Play", "Tutorial"]
        ans = self.ask(commands)
        return self.step(ans)()

    def tutorial(self):
        return self.step("Tutorial")()  # Bug: Because this calls tutorial twice, there would be 2 lines spacing

    def get_next_values(self, state, inp):
        ''' Refer to the diagram drawn 
        '''
        print('')

        if state == "Intro":
            if inp == "Intro":
                # Introductory message
                print("\nWelcome to ", self.minilode_logo)
                ans = input("press <enter> to continue: ")
                return ("Intro", ans)
            elif inp == 'skip':
                return ("Home", self.home)
            else:
                return ("Tutorial", self.tutorial)

        if state == "Tutorial":
            difficulty = 1
            game = Game(difficulty, tutorial=True)
            game.intro = "First command, enter 'display_map'"
            game.prompt = "(Tutorial) "
            game.cmdloop()

            print("\nNext time just type 'skip' to skip this tutorial!")
            print("Homepage:")
            return ("Home", self.home)

        if state == "Home":
            if inp == "Play":
                print("PLAYYYYYY")
                print("What would you like your level of difficulty to be?")
                try:
                    difficulty = int(input("1  2  3\n"))
                    if difficulty not in [1, 2, 3]:
                        raise ValueError
                except ValueError:
                    print("Please select either 1, 2, 3")
                    return self.step("Home")()
                game = Game(difficulty)
                game.prompt = "(Minilode) "
                game.cmdloop()
                return ("Home", self.home)

            elif inp == "Tutorial":
                return ("Tutorial", self.tutorial)


class Game(cmd.Cmd):
    mmap = ""
    available_directions = ["left", "right", "up", "down"]
    game_stats = {'L': 0, 'J': 0, '#': 0, 'G': 0, 'R': 0}
    _coins_type = {'L': -1000, 'J': -5, '#': -1, 'G': 25, 'R': 75}
    _coins_text = {'L': "Lava", 'J': "Junk", '#': "Dirt", 'G': "Gold", 'R': "Ruby"}
    _position = [1, 1]
    _checkpoints = {}

    _text = """Hello! Welcome to the tutorial.
    To view the next instruction, just enter 'display_map'.
    Was that hard? Hmmm next time, just press enter on an empty input to run the previous command. Try it!
    Great :)
    Now type <help or ?> followed by <command> to get more info on the commands. Eg. help display_map
    Well done!
    If you want to move down, just enter 'dig down <no. of steps>'. If no. of steps is not provided, it will default to 1. Go on, try it! Eg. dig down
    Notice that your coins decreases. Here is the legend -->  \tL: Lava, instant death!!  \tJ: Junk, -$5  \t#: Dirt, -$1  \tG: Gold, +$25  \tR: Ruby, +$75
    So what are coins for? Go back to home base to find out! Eg. dig up 2
    Home base is the first 4 tiles on the left, above ground. It's nicely demarcated by the 'H'.
    Now, type 'help store' to read up on the items, and 'store' to enter!
    Careful tho, use your coins wisely, as the player with the highest amount of coins at the end of the game wins!
    That's all that you need to know to get going :)
    Tired of typing full commands? Here's a tip: press <tab> to auto-complete input or to show list of commands available.
    Also, you can use up down keys to cycle through command history.
    Enter 'quit' to quit this tutorial.
    Oh wait... Just remembered, the blocks will all be covered with '#' instead :>
    Have fun!"""

    def __init__(self, difficulty, tutorial=False):
        super(Game, self).__init__()
        self.difficulty = difficulty
        self.tutorial = tutorial
        self._tutorial_text = (print(i) for i in self._text.split('\n'))
        self._show = tutorial  # If True, show the values
        self._items_price = {"Checkpoints": 5*self.difficulty, "Sonar": 25}  # 5, 10, 15
        self._items_inventory = {"Checkpoints": 0, "Sonar": 0}
        self._items_sonar_price = [25*3**i for i in range(self.difficulty+1)]  # 25, 75, 225, 675
        self._size = 5 + self.difficulty*10  # 15*15, 25*25, 35*35) digging ground
        self.create_map()

    def create_map(self):
        mmap = np.ndarray((self._size, self._size), dtype='<U1')
        mmap[:2, :] = ' '  # First 2 rows are for ground level
        mmap[2:, :] = '#'  # Rest are digging ground
        mmap[0, :4] = 'H'  # home
        mmap[1, 1] = 'M'  # Minilode
        self._position = [1, 1]
        self.coins = 10 + 20*self.difficulty  # 30, 50, 70 --> starting coins
        if self.tutorial:
            self.coins = 1000

        # Generate Ruby and Lava
        diff = self.difficulty-1
        for i in range(random.randint(diff*4, diff*6)):  # 0, 4-6, 8-10 --> no. of Ruby
            r_row, r_col = 0, 0
            while mmap[r_row, r_col] != '#':
                r_row = random.randint(10, self._size-3)  # Must be deep enough (ie. gives chance to buy sonar)
                r_col = random.randint(2, self._size-3)  # 2 tiles away from the game boundary
            mmap[r_row, r_col] = 'R'

            if random.randint(0, 1):
                l_row, l_col = 0, 0
                while mmap[l_row, l_col] != '#':
                    l_row = r_row + random.randint(0, 2)
                    l_col = r_col + random.randint(0, 2)

                # Replace dirt with Junk
                mmap[l_row, l_col] = 'L'

        # Generate Gold and Junk
        for i in range(5+self.difficulty*5):  # 10, 15, 20 --> no. of Gold
            # Generate Gold
            g_row, g_col = 0, 0
            while mmap[g_row, g_col] != '#':
                g_row = random.randint(2, self._size-1)
                g_col = random.randint(0, self._size-1)
            mmap[g_row, g_col] = 'G'

            # Random number of Junk
            junk = random.randint(diff+1, 5 + diff*2)  # 1-5, 2-7, 3-9
            rel = []
            for i in range(junk):
                # Junk position = gold position +/- relative position to gold position
                j_row = g_row + random.randint(-2 - diff//2, 3 + diff//2)  # 2, 2, 3
                j_col = g_col + random.randint(-2 - diff//2, 3 + diff//2)

                # Out of game area
                if j_row >= self._size or j_col >= self._size or j_row < 2 or j_col < 0:
                    continue

                # Replace dirt with Junk
                if mmap[j_row, j_col] == '#':
                    mmap[j_row, j_col] = 'J'

        self.mmap = mmap
        print("Let's go!")
        self.display_map()

    def do_display_map(self, argv):
        ''' \tWhen you type 'display_map', the current playing area would be displayed. '''
        self.display_map()

    def display_map(self):
        print(f"Cash: ${self.coins}")
        dmap = copy.deepcopy(self.mmap)

        # Display checkpoints
        for key, value in self._checkpoints.items():
            if dmap[value[0], value[1]] != 'M':
                dmap[value[0], value[1]] = str(key)

        # Print map
        for row_in, row_val in enumerate(dmap):
            print('\t', end=' ')
            for col_in, col_val in enumerate(row_val):
                # Cover up the special stones
                if col_val in self._coins_type:
                    if not self._show:
                        # if not in Sonar radius, replace it
                        if not(abs(self._position[0] - row_in) <= self._items_inventory["Sonar"]
                                and abs(self._position[1] - col_in) <= self._items_inventory["Sonar"]):
                            col_val = '#'
                print(str(col_val), end=' ')
            print('')

        if self.tutorial:
            try:
                next(self._tutorial_text)
            except StopIteration:
                pass

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

        purchase = input("\n\nWhat would you like to buy?\n").capitalize().strip()
        if purchase in items_buy:
            self.coins -= self._items_price[purchase]
            self._items_inventory[purchase] += 1

            if purchase == "Checkpoints":
                print("\nCongratulations, you just bought a checkpoint!")
                self.checkpoints()
            elif purchase == "Sonar":
                print("\nCongratulations, you just upgraded your Sonar!")
                # Update sonar price
                if self._items_inventory["Sonar"] > len(self._items_sonar_price)-1:
                    del self._items_price["Sonar"]
                else:
                    self._items_price["Sonar"] += 1

            print(f"{purchase}: {self._items_inventory[purchase]}")
            print(f"You are now left with ${self.coins}")
        else:
            print("invalid item")

    def checkpoints(self):
        # Enable or disable do_set_checkpoints method
        if self._items_inventory["Checkpoints"]:
            do_set_checkpoints = self.set_checkpoints
            do_set_checkpoints.__func__.__name__ = 'do_set_checkpoints'
            do_set_checkpoints.__func__.__qualname__ = __class__.__qualname__ + '.do_set_checkpoints'
            Game.do_set_checkpoints = do_set_checkpoints
        else:
            # No more checkpoints left
            delattr(type(self), "do_set_checkpoints")

    def set_checkpoints(self, argv):
        ''' \tSet this spot as a checkpoint '''
        self._items_inventory["Checkpoints"] -= 1
        self._checkpoints[len(self._checkpoints)+1] = copy.deepcopy(self._position)
        print(f"You are now left with {self._items_inventory['Checkpoints']} checkpoints.")

        # Enable do_teleport method
        do_teleport = self.teleport
        do_teleport.__func__.__name__ = 'do_teleport'
        do_teleport.__func__.__qualname__ = __class__.__qualname__ + '.do_teleport'
        Game.do_teleport = do_teleport
        self.checkpoints()
        self.display_map()

    def teleport(self, argv):
        '''\tTeleport minilode to this spot '''
        try:
            argv = int(argv)
        except ValueError:
            if argv == '':
                argv = "You need to specify the checkpoint no. after the command"
            print("*** Unknown syntax:", argv)
            print("Type 'help teleport' for more info")
            return

        if argv not in self._checkpoints:
            print(f"Checkpoint {argv} is not available.")
            return

        self.update_m(self._position, self._checkpoints[argv])
        self._position = self._checkpoints[argv]

        del self._checkpoints[argv]

        if not self._checkpoints:
            delattr(type(self), "do_teleport")

        self.display_map()

    def do_dig(self, direction_steps):
        ''' Get the coins in the path '''

        # Parse input
        lst = direction_steps.split(' ')  # "dig" --> [''], "dig <word>" --> ['<word>']
        if lst[0] not in self.available_directions:
            print("*** commands should be either {}".format(', '.join(self.available_directions)))
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
        except ValueError:
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

        self.update_m([row, col], self._position)

        # Add coins
        end = self.addcoins(path)
        if end:
            return end

        # Display map
        self.display_map()

    def update_m(self, old, new):
        # Update the position marking
        self.mmap[old[0], old[1]] = ' '
        self.mmap[new[0], new[1]] = 'M'

    def move(self, steps):
        # Game area is essentially _size*_size, minus the first row for HHHH markers
        for i in range(2):
            self._position[i] += steps[i]

            if self._position[i] < 1-i:  # First row is skipped
                self._position[i] = 1-i

            elif self._position[i] >= self._size:
                self._position[i] = self._size-1

    def addcoins(self, path):
        lose = False
        items = {i: 0 for i in self._coins_type}
        for i in path:
            if i == ' ':
                continue
            self.coins += self._coins_type[i]
            items[i] += 1
            self.game_stats[i] += 1
            if self.coins <= 0:
                if i == 'L':
                    print("Jeng Jeng Jenggggg")
                    print("You stepped on Lava")
                else:
                    print("Oh noes, you went out of coins...")
                print("You lose :(\n")
                lose = True
                break

        print("Items found:  ", end='')
        for key, value in items.items():
            if value != 0:
                print(f"{self._coins_text[key]}: {value}", end="  ")
        print('')

        if lose:
            return self.do_quit("Lose liaos")

    def do_quit(self, argv):
        ''' \tEnter 'quit' to quit the game '''
        self._show = True
        self.tutorial = False  # To not print the next instruction
        self.display_map()
        print("\n__Game Stats__\n")
        print("You collected: ", end='')
        total_coins = 0
        for key, value in self.game_stats.items():
            if value != 0:
                print(f"{self._coins_text[key]}: {value}", end="  ")
            if key == 'G' or key == 'R':
                total_coins += value * self._coins_type[key]
        print(f'\nTotal Coins collected: ${total_coins}')
        print("~~ Thanks for playing ~~")
        print("Bye! :)")
        return 1

    def complete_dig(self, text, line, begidx, endidx):
        # text is the string we are matching against, all returned matches must begin with it
        # line is is the current input line
        # begidx is the beginning index in the line of the text being matched
        # endidx is the end index in the line of the text being matched

        return [i+' ' for i in self.available_directions if i.startswith(text)]

    def help_dig(self):
        arr = "-->"
        print("\t{: <13} {: <7} dig <direction> <steps>".format("format", arr))
        print("\t{: <13} {: <7} {}".format("direction", arr, ', '.join(self.available_directions)))
        print("\t{: <13} {: <7} needs to be an integer".format("steps", arr))

    def help_store(self):
        print("\tWelcome to the store!")
        print("\tHere, you can buy Checkpoints or upgrade your Sonar.")
        print("\tSonar helps you to see what's underneath those dirt blocks, regardless if it's gems or a deadly path.")
        print("\tYour Sonar level tells you how far you can see around you.")
        print("\tCheckpoints are little special. This advanced piece of technology instantly teleports you to the dropped location.")
        print("\tBut haha, since it is this special, it's only one time use only.")
        print("\tWhat you waiting for? Enter 'store' on your home base (first 4 tiles above ground) to get your items now!")

    def help_set_checkpoints(self):
        print("\tTo use teleport, you must first set up the portal first.")
        print("\tDo this by entering this command to drop the checkpoint on the spot.")
        print("\tWhen you feel like it, just enter 'teleport <number>', and voilà, watch the magic unfold!")

    def help_teleport(self):
        print("\t{: <13} {: <7} teleport <number>".format("format", "-->"))
        print("\t{: <13} {: <7} number shown on the map".format("number", "-->"))


try:
    app = App()
except KeyboardInterrupt:
    print("Thanks for playing the game!")
    print("Goodbye :)")

import random
import os
import curses
import time

# will approved:tm:

"""
Format:
S - Size
G - Gender
T - Tile type
F - Food
[TT][FF][SSSS][G]

T|_0__1_
0| B  F
1| C  D
(Blank Food Creature Dead)
"""
# curses shit
stdscr = curses.initscr()
curses.noecho()
curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_GREEN)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLACK)


MUTATION_RATE = 0.0005
SIZE = slice(*(0, 4))
GENDER = slice(*(4, 5))
TILE_TYPES = {
    "B": 0b00 << 7,
    "F": 0b01 << 7,
    "C": 0b10 << 7,
    "D": 0b11 << 7,
    0: "  ",
    1: "[]",
    2: "{}",
    3: "<>",
}


def sign(value): return sorted((-1, value, 1))[1]


def int_to_bin(i, length):
    return [int(x) for x in bin(i)[2:].zfill(length)]


def bin_to_int(b):
    return int(''.join(map(str, b)), 2)


def attrib_to_bin(attrib):
    size = int_to_bin(attrib["size"], 4)
    gender = int_to_bin(attrib["gender"], 1)
    return size + gender


def bin_to_attrib(binary):
    size = bin_to_int(binary[SIZE])
    gender = bin_to_int(binary[GENDER])
    return size, gender


def mixGenes(a, b):
    a, b = list(map(str, a)), list(map(str, b))
    newgenes = int(''.join(a), 2) | int(''.join(b), 2)
    bingenes = list(bin(newgenes)[2:].zfill(4 + 1))
    return list(map(int, bingenes))


def lookup(char):
    a = int(bin(char)[2:].zfill(9)[:2], 2)
    s, g = bin_to_attrib(str(bin(char))[2:].zfill(9))
    return TILE_TYPES[a], a, curses.A_BOLD


def matrix2output(matrix):
    for row in matrix:
        for char in row:
            char, col, att = lookup(char)
            stdscr.addstr(char, curses.color_pair(col+1) + att)
        stdscr.addstr("\n", curses.color_pair(1))
    stdscr.refresh()


def makeFood(grid):
    height = len(grid)
    width = len(grid[0])
    for _ in range(0, MAX_FOOD):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        grid[y][x] = 128
    return grid


def titleScreen():

    # Declares strings to be displayed

    title = "PyEvolution Simulator"
    subtitle = "Rendered With The Curses Library"
    quit = "Press \"q\" to quit the title screen"
    continueMessage = "Press any key to continue"

    height, width = stdscr.getmaxyx()

    # Calculations for centering text

    start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
    start_x_subtitle = int((width // 2) -
                           (len(subtitle) // 2) -
                           len(subtitle) % 2)
    start_x_quit = int((width // 2) - (len(quit) // 2) - len(quit) % 2)
    start_x_continueMessage = int((width // 2) -
                                  (len(continueMessage) // 2) -
                                  len(continueMessage) % 2)
    start_y = int((height // 2) - 2)

    # Display text

    stdscr.addstr(start_y, start_x_title, title,
                  curses.color_pair(2) + curses.A_BOLD)
    stdscr.addstr(start_y + 1, start_x_subtitle,
                  subtitle, curses.color_pair(6))
    stdscr.addstr(start_y + 3, (width // 2) - 9, '=' * 18, + curses.A_BOLD)
    stdscr.addstr(start_y + 5, start_x_quit, quit)
    stdscr.addstr(start_y + 6, start_x_continueMessage, continueMessage)
    stdscr.refresh()

    # Waits for user input, and depending on the input the
    # program will close or continue

    if "q" == chr(stdscr.getch()):
        curses.endwin()
        return False
    else:
        stdscr.clear()
        stdscr.refresh()
        return True


class Tile:
    def __init__(self, type, genes=[0], food=0):
        self.tiledata = TILE_TYPES[type] | bin_to_int(genes) | (food << 5)

    @property
    def data(self):
        return self.tiledata

    def __repr__(self):
        return bin(self.data)


class DNA:
    def __init__(self, genes=None, attributes=None):
        if genes is not None:
            self.genes = genes
        elif attributes is not None:
            size = int_to_bin(attributes["size"], 4)
            gender = int_to_bin(attributes["gender"], 1)
            self.genes = size + gender

    def __repr__(self):
        return repr(self.genes)

    @property
    def size(self):
        size_bits = [str(b) for b in self.genes[SIZE]]
        size = int("".join(size_bits), 2)
        return size

    @property
    def gender(self):
        gender_bits = [str(b) for b in self.genes[GENDER]]
        gender = int("".join(gender_bits), 2)
        return gender


class Creature:
    """
    Attributes:
        - Gender (0 for male, 1 for female)
        - Food level
        - Age
        - Size
        - Speed
        - Aggression

    Fresh Creature:
        c = Creature(size=10, pos=(20, 30), mode="new")
    Child:
        c = Creature(c1, c2, mode="child")
    """
    def __init__(self, *args, **kwargs):
        if kwargs["mode"] == "child":
            self.parent1 = args[0]
            self.parent2 = args[1]
            dna = mixGenes(self.parent1, self.parent2)
            self.dna = DNA(genes=dna)
        elif kwargs["mode"] == "new":
            size = kwargs["size"]
            dna = {"size": size, "gender": random.randint(0, 1)}
            self.dna = DNA(attributes=dna)
            self.parent1 = self.dna.genes
            self.parent2 = self.dna.genes
        self.pos = list(kwargs["pos"])
        self.food = 3
        self.dead = 0
        self.cooldown = 10
        # Constant start for now

    def __repr__(self):
        attributes = ""
        for attrib in ("size", "gender"):
            attributes += f"{attrib}: {getattr(self.dna, attrib)}, "
        attributes += f"position: {self.pos}"
        output = f"<Creature({attributes})>"
        return output

    def passGenes(self):
        out = []
        for bit in zip(self.parent1, self.parent2):
            out.append(bit[random.randint(0, 1)])
        # Mutate each bit based on the mutation chance
        for i in range(len(out)):
            if random.random() < MUTATION_RATE:
                out[i] = 0 if out[i] == 1 else 1
        return out

    @property
    def tile(self):
        if self.dead:
            return Tile("D", self.dna.genes, 0)
        return Tile("C", self.dna.genes, self.food)

    def move(self):
        x, y = self.pos
        # The signing is to prevent out-of-bounds movement
        # e.g if sign(GRID_SIZE[0] - x - 1) = 0 then you shouldn't be able
        # to move to the right any further
        self.pos[0] += random.randint(sign(-x), sign(GRID_SIZE[0] - x - 1))
        self.pos[1] += random.randint(sign(-y), sign(GRID_SIZE[1] - y - 1))

    def find_food(self, grid):
        for x in range(-2, 2):
            for y in range(-2, 2):
                try:
                    testtile = grid[self.pos[1] + y][self.pos[0] + x]
                    if testtile == TILE_TYPES["F"]:
                        self.food += 1
                        return (self.pos[0] + x, self.pos[1] + y)
                except IndexError:
                    pass
        return None

    def search_mate(self, grid, creatures):
        for x in range(-2, 2):
            for y in range(-2, 2):
                try:
                    testtile = grid[self.pos[1] + y][self.pos[0] + x]
                    if testtile & 0b1 == 0:
                        partnerpos = [self.pos[0] + x, self.pos[1] + y]
                        for c in creatures:
                            if c.pos == partnerpos and c.cooldown < 1:
                                return c
                except IndexError:
                    pass
        return None


def reproduce(parent1, parent2):
    return Creature(parent1.passGenes(), parent2.passGenes(),
                    mode="child", pos=parent2.pos)


START_COUNT = 30
START_FOOD = 30
MAX_FOOD = 50
x, y = os.get_terminal_size()
GRID_SIZE = (x//2-1, y-1)


def game_iter(grid, creatures):
    for c in creatures:
        if c.dead > 0:
            c.dead += 1
            grid[c.pos[1]][c.pos[0]] = c.tile.data
            continue
        c.move()
        c.cooldown -= 1
        if random.randint(0, 100) < 13:
            c.food -= 1
        grid[c.pos[1]][c.pos[0]] = c.tile.data
        if c.food < 4:
            eaten = c.find_food(grid)
            if eaten is not None:
                grid[eaten[1]][eaten[0]] = 0
        if c.food <= 0:
            c.dead = 1
        if c.dna.gender == 1 and c.cooldown < 1:
            mate = c.search_mate(grid, creatures)
            if mate is not None:
                creatures.append(reproduce(c, mate))
                c.cooldown = 10
                mate.cooldown = 10
    return grid


if __name__ == "__main__":
    if titleScreen():
        stdscr.timeout(0)
        creatures = []
        grid = [[0 for x in range(GRID_SIZE[0])] for y in range(GRID_SIZE[1])]
        for _ in range(START_COUNT):
            size = random.randint(1, 10)
            pos = (random.randint(0, GRID_SIZE[0]-1),
                   random.randint(0, GRID_SIZE[1]-1))
            c = Creature(size=size, pos=pos, mode="new")
            creatures.append(c)
        creatures.append(reproduce(creatures[0], creatures[1]))
        while True:
            grid = [[0 for x in range(GRID_SIZE[0])]
                    for y in range(GRID_SIZE[1])]
            grid = makeFood(grid)
            grid = game_iter(grid, creatures)
            matrix2output(grid)
            def notdecomposed(c): return c.dead < 10
            creatures = list(filter(notdecomposed, creatures))
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key < 0:
                time.sleep(0.2)
            stdscr.clear()
    else:
        exit()

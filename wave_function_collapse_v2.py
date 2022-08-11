from copy import deepcopy
from PIL import Image
from pathlib import Path
from random import choice
from time import sleep

def initialisation() -> tuple:
    """Takes care of initialising the canvas, tiles, directions, etc."""

    # Prepare canvas
    img_width, img_height = 36, 24 # Width and height hardcoded for now
    canvas = Image.new('RGB', (img_width, img_height), color='white')
    canvas.save('canvas.png')

    # Load in tile set and their states
    # This can be TileSetOne or TileSetTwo
    current_tile_set = 'TileSetOne'

    pathlist = Path(current_tile_set).glob('*.png')
    TILE_STATES = [str(path).strip('TileSetOneTwo\\.png') for path in pathlist]
    pathlist = Path(current_tile_set).glob('*.png')
    TILE_SPRITES = (Image.open(path) for path in pathlist)

    TILE_WIDTH, TILE_HEIGHT = 3, 3 # Can be done automatically with PIL, hardcoded for now

    TILE_SET = dict(zip(TILE_STATES, TILE_SPRITES))

    # Generate tile array, starting at maximum entropy (when nothing has collapsed yet)
    tile_array = [[Tile(y, x, TILE_STATES.copy()) for x in range(img_width // TILE_WIDTH)] for y in range(img_height // TILE_HEIGHT)]

    # Directions for where to propogate
    DIRS_Y = (-1, 0, 1, 0)
    DIRS_X = (0, 1, 0, -1)
    
    # Where tiles between min and max entropy go
    reduced_but_not_collapsed = set()

    # A count for collapse, program ends when it hits 0 
    collapse_counter = len(tile_array) * len(tile_array[0])

    # A "savestate" for the program to rollback to in case a tile reaches 0 valid states
    # During the main loop this will be a deepcopy of the tile_array
    backup_array = []

    # Type hints for these at line ~120
    return (
    canvas, 
    TILE_STATES, 
    TILE_SET, 
    tile_array, 
    DIRS_Y, DIRS_X, 
    reduced_but_not_collapsed, 
    collapse_counter, 
    backup_array)

class Tile:
    """This represents each block/tile in the 2D array."""

    # y, x are coordinates
    # superpositions starts as a list of possible states, becomes a string when collapsed
    # is_collapsed is a flag
    def __init__(self, y: int, x: int, superpositions: list[str] | str, is_collapsed: bool = True) -> None:
        self.y = y
        self.x = x
        self.superpositions = superpositions 
        self.not_collapsed = is_collapsed

    def collapse(self) -> None:
        """Collapses current tile down to one of its superpositions and propogates this collapse to neighbouring tiles."""

        # Remove itself from reduced_but_not_collapsed, as it is undergoing collapse
        if (self.y, self.x) in reduced_but_not_collapsed:
            reduced_but_not_collapsed.remove((self.y, self.x))

        # Sets its state to one of its superpositions
        if isinstance(self.superpositions, list):
            self.superpositions = choice(self.superpositions)
        else:
            # In case of having no valid superpositions/states, load the backup and return to the loop
            global tile_array
            tile_array = backup_array
            return

        # Turn off this flag so that propogate() doesn't go to this tile (this prevent back-propogation)
        self.not_collapsed = False

        # Draws the image its state corresponds to onto the canvas
        draw_onto_canvas(self.y, self.x, self.superpositions)

        # Propogates the collapse to neighbours
        self.propagate()

        # Reduces collapse_counter
        # Program ends when this hits 0
        global collapse_counter
        collapse_counter -= 1
    
    def propagate(self) -> None:
        """Relays the collapse to surrounding tiles, reducing their states."""

        # Propogate to each neighbour tile in each direction 
        for dir_index in range(4):
            dir_y = DIRS_Y[dir_index]
            dir_x = DIRS_X[dir_index]

            # Check if coords are within bounds of the tile array 
            if -1 < self.y + dir_y < len(tile_array) \
            and -1 < self.x + dir_x < len(tile_array[0]):
                target_tile: Tile = tile_array[self.y + dir_y][self.x + dir_x]

                # only reduce_states() of tiles that aren't collapsed
                if target_tile.not_collapsed:
                    target_tile.reduce_states(dir_y, dir_x, dir_index)

    def reduce_states(self, dir_y: int, dir_x: int, dir_index: int) -> None:
        """Reduce the superpositions/states of itself, based on propogator tile.
        Number of states reaching 1 or 0 will trigger a collapse."""

        # Removing invalid states by checking with the propogator tile
        propagator_tile: Tile = tile_array[self.y - dir_y][self.x - dir_x]
        for state in self.superpositions.copy():
            if propagator_tile.superpositions[dir_index] != state[dir_index - 2]:
                self.superpositions.remove(state)

        # Trigger the collapse if it has 1 or 0 states
        if len(self.superpositions) in (1, 0):
            self.collapse()
        else:
            # Otherwise it will put itself in reduced but not collapsed
            reduced_but_not_collapsed.add((self.y, self.x))

# Unpack variables/constants from initialisation to global scope
canvas: Image.Image
TILE_STATES: list[str]
TILE_SET: dict[str, Image.Image]
tile_array: list[list[Tile]]
DIRS_Y: tuple
DIRS_X: tuple
reduced_but_not_collapsed: set
collapse_counter: int
backup_array: list[list[Tile]] # initialised as empty list

# I put initialisation in a function just for testing
(canvas,
TILE_STATES,
TILE_SET,
tile_array,
DIRS_Y, DIRS_X,
reduced_but_not_collapsed,
collapse_counter,
backup_array
) = initialisation()


def main() -> None:
    """
    Main.
    
    Bottom Text.
    """

    # In the first loop, pick a random tile to collapse
    first_loop = True
    while True:
        if first_loop:
            y = choice(range(len(tile_array)))
            x = choice(range(len(tile_array[0])))
            tile_array[y][x].collapse()
            first_loop = False
        else:
            # Setup the backup_array
            global backup_array
            backup_array = deepcopy(tile_array)

            # This is for when the program gets "stuck" (when there are no more tiles with minimum entropy/superpositions to collapse)
            # This collapses a tile with the lowest entropy
            y, x = min(reduced_but_not_collapsed, key=lambda coords: len(tile_array[coords[0]][coords[1]].superpositions))
            tile_array[y][x].collapse()
        
        # When the collapse_counter hits 0, all tiles are collapsed so the program ends
        if collapse_counter == 0:
            break    

def draw_onto_canvas(y: int, x: int, image_string: str) -> None:
    """Draws the collapsed tile onto the canvas"""

    canvas.paste(TILE_SET[image_string], (3*x, 3*y, 3*x+3, 3*y+3))    
    canvas.save('canvas.png')
    sleep(0.2)

if __name__ == '__main__':    
    main()
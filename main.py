import random
import kruskal
import prim
import binarytree as bt
import tcod

SCREEN_WIDTH = 110
SCREEN_HEIGHT = 60

TILE_SIZE = 4

MAP_ROWS = 27
MAP_WIDTH = TILE_SIZE * MAP_ROWS

MAP_COLS = 12
MAP_HEIGHT = TILE_SIZE * MAP_COLS

LIMIT_FPS = 20

FOV_ALGO = 0 # default field of view algorithm provided by tcod
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 4

class Cell:
    def __init__(self):
        self.up = True
        self.down = True
        self.right = True
        self.left = True

""" Class that takes user's input to move the player 'character' """ 
class Player:
    def __init__(self, xPos, yPos, char, color):
        self.xPos = xPos
        self.yPos = yPos
        self.char = char
        self.color = color

    def move(self, relativeX, relativeY):
        global map
        global compute_fov

        """ Check for collisions with map's wall """
        if not map[self.x + relativeX][self.y + relativeY].wall:
            self.xPos += relativeX
            self.yPos += relativeY
            map[xPos][yPos].visited = True
            compute_fov = True

        """ Update player image with new position """ 
        def draw(self, con):
            tcod.console_set_default_foreground(con, self.color)
            tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

        """ Remove player image from last position """
        def erase(self, con):
            tcod.console_put_char(con, self.x, self.y, ' ', tcod.BKGND_NONE)

""" Space occupied by each cell """
class Tile:
    def __init__(self, is_wall):
        self.wall = is_wall
        self.explored = False
        self.visited = False


def makeMap(cells):
    global map

    map = [[ Tile(False)
        for y in range(MAP_HEIGHT)]
        for x in range(MAP_WIDTH)]

    """ Setting map boundaries in y. """
    for y in range(MAP_HEIGHT):
        map[0][y].wall = True
        map[0][y].explored = True
        map[MAP_WIDTH - 1][y].wall = True
        map[MAP_WIDTH - 1][y].explored = True


    """ Setting map boundaries in x. """
    for x in range(MAP_WIDTH):
        map[x][0].wall = True
        map[x][0].explored = True
        map[x][MAP_HEIGHT - 1].explored = True 


    """ Generating walls for each tile. """
    for x in range(MAP_ROWS):
        for y in range(MAP_COLS):
            map[x * TILE_SIZE][y * TILE_SIZE].wall = True
            map[x * TILE_SIZE][(y+1) * TILE_SIZE - 1].wall = True
            map[(x+1) * TILE_SIZE - 1][y * TILE_SIZE].wall = True
            map[(x+1) * TILE_SIZE - 1][(y+1) * TILE_SIZE - 1].wall = True

            for k in range(1, TILE_SIZE - 1):
                map[x * TILE_SIZE][y * TILE_SIZE + k].wall = cells[x][y].up
                map[x * TILE_SIZE + k][y * TILE_SIZE] = cells[x][y].left
                map[x * TILE_SIZE + k][(y+1) * TILE_SIZE - 1] = cells[x][y].right
                map[(x+1) * TILE_SIZE - 1][y * TILE_SIZE + k] = cells[x][y].down


def eraseMap(con):
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            tcod.console_put_char_ex(con, x, y, ' ', tcod.white, tcod.black)


def render(player, con, fov_map, check_explored):
    tcod.map_compute_fov(fov_map, player.xPos, player.yPos, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            visible = tcod.map_is_in_fov(fov_map, x, y)
            compute_fov = False
            wall = map[x][y].wall
            if not visible and (map[x][y].explored or not check_explored):
                if check_explored:
                    color = tcod.grey
                else:
                    color = tcod.light_grey
            
                if wall:
                    tcod.console_put_char_ex(con, x, y, '#', color, tcod.black)
                else:
                    tcod.console_put_char_ex(con, x, y, '.', color, tcod.black)

            if visible:
                map[x][y].explored = True
                if wall:
                    tcod.console_put_char_ex(con, x, y, '#', tcod.light_yellow, tcod.black)
                else:
                    tcod.console_put_char_ex(con, x, y, '.', tcod.light_yellow, tcod.black)

    tcod.console_put_char_ex(con, MAP_WIDTH-2, MAP_HEIGHT-2, 'X', tcod.fuchsia, tcod.black)
    player.draw(con)


def keyboard_input(player, con):

    global fog_of_war
    key = tcod.console_wait_for_keypress(True)

    if key.vk == tcod.KEY_ESCAPE:
        return True

    if key.vk == tcod.KEY_SPACE:
        fog_of_war = not fog_of_war
        eraseMap(con)

    if tcod.console_is_key_pressed(tcod.KEY_UP):
        player.move(0, 1)

    if tcod.console_is_key_pressed(tcod.KEY_DOWN):
        player.move(0, -1)

    if tcod.console_is_key_pressed(tcod.KEY_LEFT):
        player.move(-1, 0)

    if tcod.console_is_key_pressed(tcod.KEY_RIGHT):
        player.move(1, 0)

    return False


def main():
    
    player = Player(1, 1, 'O', tcod.green)

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Maze', False, tcod.RENDERER_SDL2)

    con = tcod.console.Console(MAP_WIDTH, MAP_HEIGHT)
    tcod.sys_set_fps(LIMIT_FPS)

    fov_map = tcod.map.Map(MAP_WIDTH, MAP_HEIGHT)
    global compute_fov
    compute_fov = False

    cells = [[ Cell()
        for y in range(MAP_COLS)]
        for x in range(MAP_ROWS)]

    makeMap(cells)

    choice = 0

    (wall_set, cells_finished, cells) = prim.init_variables(MAP_ROWS, MAP_COLS)

    while len(cells_finished) != MAP_ROWS*MAP_COLS:
        cells = prim.generate_maze(wall_set, cells_finished, cells, MAP_ROWS, MAP_COLS)

    makeMap(cells)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            fov_map.walkable[:]
            fov_map.transparent[:]
            
    render(player, con, fov_map, True)
    tcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
    tcod.console_flush()

    while not tcod.console_is_window_closed():

        if player.xPos == MAP_WIDTH-2 and player.yPos == MAP_HEIGHT-2:
            render(player, con, fov_map, False)
            tcod.console_put_char_ex(con, 1, 1, 'S', tcod.pink, tcod.black)
            player.draw(con)
            tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
            tcod.console_flush()

            key = tcod.console_wait_for_keypress(True)
            break

        render(player, con, fov_map, fog_of_war)

        tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        tcod.console_flush()

        player.erase(con)

        quit = keyboard_input(player, con)

        if quit:
            render(player, con, fov_map, True, qui)
            tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
            tcod.console_flush()

            key = tcod.console_wait_for_keypress(True)

            if key.vk == tcod.KEY_ESCAPE:
                render(player, con, fov_map, False, qui)
                player.draw(con)
                tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
                tcod.console_flush()

                key = tcod.console_wait_for_keypress(True)
                break

if __name__ == '__main__':
    main()
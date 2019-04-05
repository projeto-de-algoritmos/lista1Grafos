import random
import kruskal
import prim
import binarytree as bt
import tcod as libtcod

SCREEN_WIDTH = 110
SCREEN_HEIGHT = 60

TILE_SIZE = 4

MAP_ROWS = 27
MAP_WIDTH = TILE_SIZE * MAP_ROWS

MAP_COLS = 12
MAP_HEIGHT = TILE_SIZE * MAP_COLS

PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

LIMIT_FPS = 20

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

        """ Check for collisions with map's wall """
        if not map[self.x + relativeX][self.y + relativeY].wall:
            self.xPos += relativeX
            self.yPos += relativeY
            map[xPos][yPos].visited = True

        """ Update player image with new position """ 
        def draw(self, con):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

        """ Remove player image from last position """
        def erase(self, con):
            libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Tile:
    def __init__(self, is_wall):
        self.wall = is_wall
        self.explored = False
        self.visited = False
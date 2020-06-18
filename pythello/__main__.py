import sys

import pygame as pg

from pythello.app import App
from pythello.pythello import game, size

if __name__ == '__main__':
    pg.init()
    App(game, size).start()
    pg.quit()
    sys.exit()

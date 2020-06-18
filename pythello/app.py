from itertools import product
import pygame as pg
import pygame_gui as pgui
from pygame import gfxdraw
from pythello.player import AI


CAPTION = 'Pythello'
PLAYER1_COLOR = pg.Color('black')
PLAYER2_COLOR = pg.Color('white')
MOVE_COLOR = pg.Color('green')
BOARD_COLOR = pg.Color('forestgreen')
GRID_COLOR = pg.Color('black')


class App:
    def __init__(self, game, size):
        self.game = game
        self.grid_size = int(size // game.board.size)
        self.radius = int(self.grid_size // 2.5)
        self.move_radius = self.grid_size // 8
        self.menu_height = 25

        self.running = True
        self.paused = True
        self.game_over = False
        self.turn = 0
        self.time_since_turn = 0
        self.ai_delay = 200

        screen_size = size, size + self.menu_height
        self.screen = pg.display.set_mode(screen_size)
        self.board = pg.Surface((size, size))
        self.manager = pgui.UIManager(screen_size)
        self.add_ui()
        self.draw_board()

    def add_ui(self):
        board_width = self.board.get_width()
        label_width = 80

        pos = board_width - 2 * self.menu_height - label_width
        size_down = pg.Rect(pos, 0, self.menu_height, self.menu_height)
        pgui.elements.UIButton(size_down, '◀', self.manager, object_id='size_down')

        pos = board_width - self.menu_height - label_width
        size_rect = pg.Rect(pos, 0, label_width, self.menu_height)
        size_str = f'Size: {self.game.board.size}'
        self.size_label = pgui.elements.UILabel(size_rect, size_str, self.manager)

        pos = board_width - self.menu_height
        size_up = pg.Rect(pos, 0, self.menu_height, self.menu_height)
        pgui.elements.UIButton(size_up, '▶', self.manager, object_id='size_up')

    @property
    def ai_turn(self):
        return isinstance(self.game.player, AI) and not self.game_over

    def change_size(self, size):
        if size >= 4:
            self.game._board = GridBoard(size)
            self.grid_size = int(self.board.get_width() // size)
            self.radius = int(self.grid_size // 2.5)
            self.move_radius = self.grid_size // 8
            self.size_label.set_text(f'Size: {size}')
            self.reset()

    def draw_board(self):
        self.board.fill(BOARD_COLOR)
        width, height = self.board.get_size()
        grid_width = self.grid_size // 20

        for r, c in product(range(self.game.board.size-1), range(self.game.board.size-1)):
            x = (c + 1) * self.grid_size
            y = (r + 1) * self.grid_size
            pg.draw.line(self.board, GRID_COLOR, (x, 0), (x, height), grid_width)
            pg.draw.line(self.board, GRID_COLOR, (0, y), (width, y), grid_width)

    def draw_circle(self, row, col, radius, color):
        x = col * self.grid_size + self.grid_size // 2
        y = row * self.grid_size + self.grid_size // 2 + self.menu_height
        gfxdraw.aacircle(self.screen, x, y, radius, color)
        gfxdraw.filled_circle(self.screen, x, y, radius, color)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.handle_key(event.key)
            elif event.type == pg.USEREVENT:
                self.handle_ui(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                move = (event.pos[1] - self.menu_height) // self.grid_size, event.pos[0] // self.grid_size

                if move in self.game.valid:
                    self.make_move(move)

            self.manager.process_events(event)

    def handle_key(self, key):
        if key == pg.K_SPACE:
            self.paused = not self.paused
            self.time_since_turn = 0
        elif key == pg.K_TAB:
            self.paused = True

            if self.ai_turn:
                self.make_move()
        elif key == pg.K_BACKSPACE:
            self.reset()
        elif key == pg.K_UP:
            self.change_size(self.game.board.size + 2)
        elif key == pg.K_DOWN:
            self.change_size(self.game.board.size - 2)

    def handle_ui(self, event):
        if event.user_type == pgui.UI_BUTTON_PRESSED:
            if event.ui_object_id == 'size_up':
                self.change_size(self.game.board.size + 2)
            elif event.ui_object_id == 'size_down':
                self.change_size(self.game.board.size - 2)

    def make_move(self, move=None):
        if move is None:
            move = self.game.player.move(self.game)

        self.game.move(move)
        self.game_over = self.game.is_over()
        self.turn += 1
        self.time_since_turn = 0

    def render(self):
        pg.display.set_caption(f'{CAPTION}: Turn {self.turn}')
        self.screen.blit(self.board, (0, self.menu_height))

        # draw player 1 pieces
        for row, col in zip(*self.game.board.get_pieces(1)):
            self.draw_circle(row, col, self.radius, PLAYER1_COLOR)

        # draw player 2 pieces
        for row, col in zip(*self.game.board.get_pieces(-1)):
            self.draw_circle(row, col, self.radius, PLAYER2_COLOR)

        # draw valid moves
        for row, col in self.game.valid:
            self.draw_circle(row, col, self.move_radius, MOVE_COLOR)

        self.manager.draw_ui(self.screen)
        pg.display.update()

    def reset(self):
        self.game.reset()
        self.game_over = False
        self.turn = 0
        self.time_since_turn = 0
        self.draw_board()

    def start(self):
        clock = pg.time.Clock()
        tick = 0

        while self.running:
            self.event_loop()
            self.update(tick)
            self.render()
            tick = clock.tick()

    def update(self, time):
        self.manager.update(time)

        if self.ai_turn and not self.paused:
            if self.time_since_turn > self.ai_delay:
                self.make_move()
            else:
                self.time_since_turn += time

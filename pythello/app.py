from __future__ import annotations

from itertools import product
from typing import TYPE_CHECKING

import pygame as pg
import pygame_gui as pgui
from pygame import gfxdraw

from pythello.board import Board, Color, position_to_coordinates
from pythello.game import Game
from pythello.player import AI

if TYPE_CHECKING:
    from pythello.board import Position
    from pythello.player import Player

CAPTION = 'Pythello'
PLAYER1_COLOR = pg.Color('black')
PLAYER2_COLOR = pg.Color('white')
MOVE_COLOR = pg.Color('green')
BOARD_COLOR = pg.Color('forestgreen')
GRID_COLOR = pg.Color('black')
BACKGROUND_COLOR = pg.Color('black')
GRAPH_LINE_COLOR = pg.Color('white')
TEXT_COLOR = pg.Color('black')


class App:
    def __init__(self, size: int) -> None:
        self.game = Game(Board())
        self.size = size
        self.menu_height = 25
        self.graph_height = 100

        self.running = True
        self.paused = True
        self.turn = 0
        self.time_since_turn = 0
        self.ai_delay = 200

        screen_size = size, size + self.menu_height
        self.screen = pg.display.set_mode(screen_size)
        self.background = pg.Surface((size, self.menu_height))
        self.background.fill(BACKGROUND_COLOR)
        self.board = pg.Surface((size, size))
        self.graph = pg.Surface((size, self.graph_height))
        self.manager = pgui.UIManager(screen_size)
        self.font = pg.font.SysFont(None, 25)
        self.add_ui()
        self.draw_board()
        self.draw_graph()

    def add_ui(self) -> None:
        elem_width = (self.size - 4 * self.menu_height) / 5
        player_options = ['HUMAN'] + [player.name for player in AI]

        pos = self.size - 2 * self.menu_height - elem_width
        size_down = pg.Rect(pos, 0, self.menu_height, self.menu_height)
        pgui.elements.UIButton(size_down, '◀', self.manager, object_id='size_down')

        pos = self.size - self.menu_height - elem_width
        size_rect = pg.Rect(pos, 0, elem_width, self.menu_height)
        size_str = f'Size: {self.game.board.size}'
        self.size_label = pgui.elements.UILabel(size_rect, size_str, self.manager)

        pos = self.size - self.menu_height
        size_up = pg.Rect(pos, 0, self.menu_height, self.menu_height)
        pgui.elements.UIButton(size_up, '▶', self.manager, object_id='size_up')

        pos = self.size - 2 * self.menu_height - 2 * elem_width
        show_graph = pg.Rect(pos, 0, elem_width, self.menu_height)
        self.show_graph = pgui.elements.UIButton(
            show_graph, 'Show Graph', self.manager, object_id='show_graph'
        )

        pos = self.size - 2 * self.menu_height - 3 * elem_width
        show_gain = pg.Rect(pos, 0, elem_width, self.menu_height)
        self.show_gain = pgui.elements.UIButton(
            show_gain, 'Show Gain', self.manager, object_id='show_gain'
        )

        player1_score = pg.Rect(elem_width, 0, self.menu_height, self.menu_height)
        self.player1_score = pgui.elements.UILabel(player1_score, '2', self.manager)

        pos = elem_width + self.menu_height
        player2_score = pg.Rect(pos, 0, self.menu_height, self.menu_height)
        self.player2_score = pgui.elements.UILabel(player2_score, '2', self.manager)

        player1_select = pg.Rect(0, 0, elem_width, self.menu_height)
        pgui.elements.UIDropDownMenu(
            player_options,
            self.game.players[0].name,
            player1_select,
            self.manager,
            object_id='player1',
        )

        pos = elem_width + 2 * self.menu_height
        player2_select = pg.Rect(pos, 0, elem_width, self.menu_height)
        pgui.elements.UIDropDownMenu(
            player_options,
            self.game.players[1].name,
            player2_select,
            self.manager,
            object_id='player2',
        )

    def change_game(
        self,
        player1: Player | None = None,
        player2: Player | None = None,
        size: int | None = None,
    ) -> None:
        change = False

        if player1 is None:
            player1 = self.game.players[0].player
        elif player1 != self.game.players[0].player:
            change = True

        if player2 is None:
            player2 = self.game.players[1].player
        elif player2 != self.game.players[1].player:
            change = True

        if size is None:
            board = self.game.board
        elif size != self.game.board.size and size >= 4:
            board = Board(size)
            change = True

        if change:
            self.game = Game(board, player1, player2)
            self.size_label.set_text(f'Size: {board.size}')
            self.paused = True
            self.reset()

    def draw_board(self) -> None:
        self.board.fill(BOARD_COLOR)
        grid_width = self.grid_size // 20
        grid_iter = range(self.game.board.size - 1)

        for r, c in product(grid_iter, grid_iter):
            x = (c + 1) * self.grid_size
            y = (r + 1) * self.grid_size
            pg.draw.line(self.board, GRID_COLOR, (x, 0), (x, self.size), grid_width)
            pg.draw.line(self.board, GRID_COLOR, (0, y), (self.size, y), grid_width)

    def draw_circle(
        self, surface: pg.Surface, x: int, y: int, radius: int, color: pg.Color
    ) -> None:
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)

    def draw_graph(self) -> None:
        self.graph.fill(BACKGROUND_COLOR)
        h = self.graph_height / 2
        a = (0, h)
        b = (self.size, h)
        pg.draw.line(self.graph, GRAPH_LINE_COLOR, a, b, 1)

    def draw_piece(self, position: Position, radius: int, color: pg.Color) -> None:
        x, y = self.get_grid_coords(position)
        self.draw_circle(self.screen, x, y, radius, color)

    def draw_score_gain(self, position: Position) -> None:
        pieces_gained = len(self.game.captured(position))
        textsurface = self.font.render(str(pieces_gained), True, TEXT_COLOR)
        x, y = self.get_grid_coords(position)
        x -= textsurface.get_width() / 2 - 1
        y -= textsurface.get_height() / 2 - 1
        self.screen.blit(textsurface, (x, y))

    def event_loop(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.handle_key(event.key)
            elif event.type == pg.USEREVENT:
                self.handle_ui(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                row = (event.pos[1] - self.menu_height) // self.grid_size
                col = event.pos[0] // self.grid_size
                valid_row = 0 <= row <= self.game.board.size - 1
                valid_col = 0 <= col <= self.game.board.size - 1
                move = (
                    1 << row * self.game.board.size + col
                    if valid_row and valid_col
                    else None
                )

                if move in self.game.valid:
                    self.make_move(move)

            self.manager.process_events(event)

    def get_grid_coords(self, position: Position) -> tuple[int, int]:
        row, col = position_to_coordinates(position, self.game.board.size)
        x = col * self.grid_size + self.grid_size // 2
        y = row * self.grid_size + self.grid_size // 2 + self.menu_height
        return x, y

    @property
    def grid_size(self) -> int:
        return int(self.size // self.game.board.size)

    def handle_key(self, key: int) -> None:
        if key == pg.K_SPACE:
            self.paused = not self.paused
            self.time_since_turn = 0
        elif key == pg.K_TAB:
            self.paused = True

            if self.game.ai_turn and not self.game.is_over:
                self.make_move()
        elif key == pg.K_BACKSPACE:
            self.reset()
        elif key == pg.K_UP:
            self.change_game(size=self.game.board.size + 2)
        elif key == pg.K_DOWN:
            self.change_game(size=self.game.board.size - 2)

    def handle_ui(self, event: pg.event.Event) -> None:
        if event.user_type == pgui.UI_BUTTON_PRESSED:
            if event.ui_object_id == 'size_up':
                self.change_game(size=self.game.board.size + 2)
            elif event.ui_object_id == 'size_down':
                self.change_game(size=self.game.board.size - 2)
            elif event.ui_object_id == 'show_graph':
                if self.show_graph.is_selected:
                    self.show_graph.unselect()
                    screen_size = self.size, self.size + self.menu_height
                else:
                    self.show_graph.select()
                    screen_size = (
                        self.size,
                        self.size + self.menu_height + self.graph_height,
                    )

                self.screen = pg.display.set_mode(screen_size)
            elif event.ui_object_id == 'show_gain':
                if self.show_gain.is_selected:
                    self.show_gain.unselect()
                else:
                    self.show_gain.select()
        elif event.user_type == pgui.UI_DROP_DOWN_MENU_CHANGED:
            ai_players = {player.name for player in AI}
            player = AI[event.text] if event.text in ai_players else event.text
            self.change_game(**{event.ui_object_id: player})

    def make_move(self, move: Position | None = None) -> None:
        self.game.move(move)

        if self.game.is_over:
            self.game.print_results()

        self.turn += 1
        self.time_since_turn = 0
        self.update_graph()
        self.update_score()

    @property
    def move_radius(self) -> int:
        return self.grid_size // 8

    @property
    def radius(self) -> int:
        return int(self.grid_size // 2.5)

    def render(self) -> None:
        pg.display.set_caption(f'{CAPTION}: Turn {self.turn}')
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.board, (0, self.menu_height))

        if self.show_graph.is_selected:
            self.screen.blit(self.graph, (0, self.menu_height + self.size))

        # draw player 1 pieces
        for position in self.game.board.player_pieces(Color.BLACK):
            self.draw_piece(position, self.radius, PLAYER1_COLOR)

        # draw player 2 pieces
        for position in self.game.board.player_pieces(Color.WHITE):
            self.draw_piece(position, self.radius, PLAYER2_COLOR)

        # draw valid moves
        for position in self.game.valid:
            self.draw_piece(position, self.move_radius, MOVE_COLOR)

            if self.show_gain.is_selected:
                self.draw_score_gain(position)

        self.manager.draw_ui(self.screen)
        pg.display.update()

    def reset(self) -> None:
        self.game.reset()
        self.turn = 0
        self.time_since_turn = 0
        self.draw_board()
        self.draw_graph()
        self.update_score()

    def start(self) -> None:
        clock = pg.time.Clock()
        tick = 0

        while self.running:
            self.event_loop()
            self.update(tick)
            self.render()
            tick = clock.tick()

    def update(self, time: int) -> None:
        self.manager.update(time)

        if self.game.ai_turn and not self.game.is_over and not self.paused:
            if self.time_since_turn > self.ai_delay:
                self.make_move()
            else:
                self.time_since_turn += time

    def update_graph(self) -> None:
        n = self.game.board.size**2
        h = self.graph_height
        w = self.size - self.size / (n - 4)

        x = w * self.turn / (n - 4)
        y1 = h / 2
        y2 = h * (-self.game.score[-1] + n) / (2 * n)

        pg.draw.line(self.graph, GRAPH_LINE_COLOR, (x, y1), (x, y2), 2)
        self.draw_circle(self.graph, int(round(x)), int(round(y2)), 3, GRAPH_LINE_COLOR)

    def update_score(self) -> None:
        self.player1_score.set_text(str(self.game.board.player_score(Color.BLACK)))
        self.player2_score.set_text(str(self.game.board.player_score(Color.WHITE)))

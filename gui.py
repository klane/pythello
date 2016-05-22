import numpy as np
import tkinter as tk
from player import AI


class GUI(tk.Frame):
    def __init__(self, game, size, margin, master=None):
        tk.Frame.__init__(self, master)
        self.game = game
        self.cell_size = (size - 2*margin) / self.game.size
        self.coordinates = lambda position: self.cell_size * (np.asarray(position) + 1/2) + margin
        self.grid()
        self.master.title("Pythello")
        self.canvas = tk.Canvas(self, width=size, height=size, background='#333', highlightthickness=0)
        self.canvas.create_rectangle(margin, margin, size - margin, size - margin, outline='white')
        self.refresh()
        reset = tk.Button(self, text='Reset', command=self.reset)

        if any([not isinstance(player, AI) for player in [self.game.player1, self.game.player2]]):
            self.canvas.grid(row=0, column=0)
            reset.grid(row=1, column=0)
        else:
            self.canvas.grid(row=0, column=0, columnspan=2)
            reset.grid(row=1, column=1)
            tk.Button(self, text='Run', command=self.move).grid(row=1, column=0)

        for i in range(self.game.size):
            line_shift = self.cell_size * (i+1) + margin
            self.canvas.create_text(margin-10, line_shift - self.cell_size/2, text=str(i+1), fill='white')
            self.canvas.create_text(line_shift - self.cell_size/2, margin-10, text=chr(97+i), fill='white')
            self.canvas.create_line(margin, line_shift, size - margin, line_shift, fill='white')
            self.canvas.create_line(line_shift, margin, line_shift, size - margin, fill='white')

    def draw_piece(self, position, radius, color):
        (y, x) = self.coordinates(position)
        return self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, tags='circle')

    def move(self, pause=10, event=None):
        if event is None:
            self.game.move(self.game.current_player)
        else:
            move = eval(self.canvas.gettags(event.widget.find_withtag("current"))[-2])
            self.game.move(self.game.current_player, move)

        self.refresh()

        if isinstance(self.game.current_player, AI) and not self.game.game_over():
            self.after(pause, self.move)

    def refresh(self):
        [self.canvas.delete(tag) for tag in ['circle', 'text']]

        for position in zip(*np.nonzero(self.game.board)):
            self.draw_piece(position, (self.cell_size-2) / 2, self.game.players[self.game.board[position]].color)

        if not isinstance(self.game.current_player, AI):
            for position in self.game.valid:
                (y, x) = self.coordinates(position)
                turned = len(self.game.valid[position]) - 1
                valid = self.draw_piece(position, self.cell_size / 4, 'green')
                self.canvas.addtag(str(position), 'withtag', valid)
                text = self.canvas.create_text(x+1, y+1, text=str(turned), tags=('text', str(position)))
                [self.canvas.tag_bind(tag, "<Button-1>", lambda event: self.move(1000, event)) for tag in [valid, text]]

    def reset(self):
        self.game.reset()
        self.refresh()

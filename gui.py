import numpy as np
from player import AI
from tkinter import Button, Canvas, Frame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GUI(Frame):
    def __init__(self, game, size, margin, colors=('black', 'white'), master=None):
        color = '#333333'
        Frame.__init__(self, master, bg=color)
        self.game = game
        self.cell_size = (size - 2*margin) / self.game.size
        self.coordinates = lambda position: self.cell_size * (np.array(position) + 1/2) + margin
        self.grid()
        self.master.title("Pythello")
        self.colors = colors

        max_turns = self.game.size**2 - 4
        figure = Figure(figsize=(size/100, size/100), dpi=100, facecolor=color)
        axes = figure.add_subplot(111, axisbg=color)
        self.line = axes.plot(0, 0, 'w-', [0, max_turns], [0, 0], 'w--')[0]
        axes.grid(True, color='w')
        axes.set_xlim(0, max_turns)
        axes.set_ylim(-max_turns, max_turns)
        [tick.set_color('w') for axis in [axes.xaxis, axes.yaxis] for tick in axis.get_ticklines()]
        [label.set_color('w') for axis in [axes.xaxis, axes.yaxis] for label in axis.get_ticklabels()]
        [axes.spines[side].set_color('w') for side in ['top', 'bottom', 'left', 'right']]

        self.canvas = Canvas(self, width=size, height=size, background=color, highlightthickness=0)
        self.canvas.create_rectangle(margin, margin, size - margin, size - margin, outline='white')
        self.canvas.grid(row=0, column=1, rowspan=50)
        self.figure = FigureCanvasTkAgg(figure, master=self)
        self.figure.get_tk_widget().grid(row=0, column=2, rowspan=50)
        self.refresh()
        row = 1 if all([isinstance(player, AI) for player in [self.game.player1, self.game.player2]]) else 0
        Button(self, text='Reset', command=self.reset).grid(row=row, column=0)

        if row == 1:
            Button(self, text='Run', command=self.move).grid(row=0, column=0)

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
            move = self.game.current_player.move(self.game)
        else:
            move = eval(self.canvas.gettags(event.widget.find_withtag("current"))[-2])

        self.game.move(self.game.current_player, move)
        self.refresh()

        if isinstance(self.game.current_player, AI) and not self.game.game_over():
            self.after(pause, self.move)

    def refresh(self):
        self.line.set_data(range(len(self.game.score)), self.game.score)
        self.figure.draw()
        [self.canvas.delete(tag) for tag in ['circle', 'text']]

        for position in zip(*np.nonzero(self.game.board)):
            color = self.colors[self.game.players[self.game.board[position]].number - 1]
            self.draw_piece(position, (self.cell_size-2) / 2, color)

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

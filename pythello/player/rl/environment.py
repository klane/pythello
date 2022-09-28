from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from gym.spaces import Box, Dict, Discrete, MultiBinary
from ray.rllib.env import MultiAgentEnv

from pythello.board import Board, Color, position_index, split_position
from pythello.board.board import DEFAULT_SIZE
from pythello.game import Game, Result

if TYPE_CHECKING:
    from ray.rllib.utils.typing import MultiAgentDict

WIN_REWARD = 10
LOSS_REWARD = -WIN_REWARD
DRAW_REWARD = 1
REWARDS = {
    Result.WIN: WIN_REWARD,
    Result.LOSS: LOSS_REWARD,
    Result.DRAW: DRAW_REWARD,
}


class Environment(MultiAgentEnv):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__()

        board_size = config.get('board_size', DEFAULT_SIZE)
        self.game = Game(Board(board_size))

        num_players = 2
        self._agent_ids = set(range(num_players))

        num_spaces = board_size**2
        self.action_space = Discrete(num_spaces)

        self._action_mask = Box(0, 1, shape=(num_spaces,))
        # self._observation_space = Box(-1, 1, shape=(num_spaces,), dtype=np.int8)
        self._observation_space = MultiBinary((num_players, num_spaces))
        self.observation_space = Dict(
            {
                'action_mask': self._action_mask,
                'observations': self._observation_space,
            }
        )

    def reset(self) -> MultiAgentDict:
        self.game.reset()
        player = self.game.current_player.color
        return {player: self._current_observations(player)}

    def step(
        self, actions: MultiAgentDict
    ) -> tuple[MultiAgentDict, MultiAgentDict, MultiAgentDict, MultiAgentDict]:
        if len(actions) > 1:
            raise ValueError('Only one player can move at a time')
        elif len(actions) == 1:
            # get action
            player, move = actions.copy().popitem()

            if player is not self.game.current_player.color:
                name = Color(player).name
                raise ValueError(f'{name.title()} is not the current player')

            # make move and pass if next player has no valid moves
            move = 1 << int(move)
            self.game.move(move)

        obs, rew, done, info = {}, {}, {}, {}

        # compute observations for current player
        # current player is the one that has the next move, not the one that just moved
        player = self.game.current_player.color
        obs[player] = self._current_observations(player)

        # check if game is over
        game_over = self.game.is_over

        # all agents are done when the game is over
        for x in list(Color) + ['__all__']:
            done[x] = game_over

        if game_over:
            # add observation to enable info for both players
            obs[player.opponent] = self._current_observations(player.opponent)

            # provide rewards and info
            for player in Color:
                result = self.game.result(player)

                if result is None:
                    raise ValueError('The game is not finished')

                rew[player] = REWARDS[result]
                info[player] = {'result': result}

        return obs, rew, done, info

    def _current_observations(self, player: Color) -> dict[str, np.ndarray]:
        action_mask = np.zeros_like(self._action_mask.sample())
        observations = np.zeros_like(self._observation_space.sample())

        for i in self.game.board.valid_moves(player):
            action_mask[position_index(i)] = 1

        # # for m in split_position(self.game.board.players[player]):
        # for m in split_position(self.game.board.players[Color.BLACK]):
        #     observations[position_index(m)] = 1

        # # for m in split_position(self.game.board.players[player.opponent]):
        # for m in split_position(self.game.board.players[Color.WHITE]):
        #     observations[position_index(m)] = -1

        for i, position in enumerate(self.game.board.players):
            for m in split_position(position):
                # observations[position_index(m)] = 1 if i == player else -1
                observations[i, position_index(m)] = 1

        return {'action_mask': action_mask, 'observations': observations}

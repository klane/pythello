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
        self._game = Game(Board(board_size))
        self._agent_ids = set(Color)

        num_spaces = board_size**2
        self.action_space = Discrete(num_spaces)
        self.observation_space = Dict(
            {
                'action_mask': Box(0, 1, shape=(num_spaces,), dtype=np.int8),
                # 'observation': Box(-1, 1, shape=(num_spaces,), dtype=np.int8),
                'observation': MultiBinary((len(Color), num_spaces)),
            }
        )

    def compute_observation(self, game: Game, player: Color) -> dict[str, np.ndarray]:
        observation = self.observation_space.sample()
        observation['action_mask'].fill(0)
        observation['observation'].fill(0)

        for i in game.board.valid_moves(player):
            observation['action_mask'][position_index(i)] = 1

        # # for m in split_position(self._game.board.players[player]):
        # for m in split_position(self._game.board.players[Color.BLACK]):
        #     observation['observation'][position_index(m)] = 1

        # # for m in split_position(self._game.board.players[player.opponent]):
        # for m in split_position(self._game.board.players[Color.WHITE]):
        #     observation['observation'][position_index(m)] = -1

        for i, position in enumerate(game.board.players):
            for m in split_position(position):
                # observation['observation'][position_index(m)] = 1 if i == player else -1
                observation['observation'][i, position_index(m)] = 1

        return observation

    def reset(self) -> MultiAgentDict:
        self._game.reset()
        player = self._game.current_player.color
        return {player: self.compute_observation(self._game, player)}

    def step(
        self, actions: MultiAgentDict
    ) -> tuple[MultiAgentDict, MultiAgentDict, MultiAgentDict, MultiAgentDict]:
        if len(actions) > 1:
            raise ValueError('Only one player can move at a time')
        elif len(actions) == 1:
            # get action
            player, move = actions.copy().popitem()

            if player is not self._game.current_player.color:
                name = Color(player).name
                raise ValueError(f'{name.title()} is not the current player')

            # make move and pass if next player has no valid moves
            move = 1 << int(move)
            self._game.move(move)

        obs, rew, done, info = {}, {}, {}, {}

        # compute observation for current player
        # current player is the one that has the next move, not the one that just moved
        player = self._game.current_player.color
        obs[player] = self.compute_observation(self._game, player)

        # check if game is over
        game_over = self._game.is_over

        # all agents are done when the game is over
        done = {Color.BLACK: game_over, Color.WHITE: game_over, '__all__': game_over}

        if game_over:
            # add opponent observation to enable info for both players
            opponent = player.opponent
            obs[opponent] = self.compute_observation(self._game, opponent)

            # provide rewards and info
            for player in Color:
                result = self._game.result(player)
                rew[player] = REWARDS[result]
                info[player] = {'result': result}

        return obs, rew, done, info

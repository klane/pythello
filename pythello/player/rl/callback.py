from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction
from typing import TYPE_CHECKING, Any, NamedTuple

import numpy as np
from ray.rllib.algorithms.callbacks import DefaultCallbacks

from pythello.board import Color
from pythello.game import Result

from .environment import DRAW_REWARD, LOSS_REWARD, WIN_REWARD

if TYPE_CHECKING:
    from ray.rllib.algorithms import Algorithm
    from ray.rllib.evaluation import Episode, RolloutWorker
    from ray.rllib.utils.typing import AgentID, PolicyID

OPPONENT_REWARDS = {
    WIN_REWARD: Result.LOSS,
    LOSS_REWARD: Result.WIN,
    DRAW_REWARD: Result.DRAW,
}


class Percent(Fraction):
    def append(self, condition: bool) -> None:
        self._denominator += 1

        if condition:
            self._numerator += 1

    @classmethod
    def new(cls) -> Percent:
        pct = cls()
        pct._denominator -= 1
        return pct


class Summary(NamedTuple):
    player: Color
    opponent: str
    result: Result


class SelfPlayCallback(DefaultCallbacks):
    def __init__(self, win_rate_threshold: float, episode_window: int = 1000) -> None:
        if not 0 <= win_rate_threshold <= 1:
            raise ValueError('Win rate threshold must be between 0 and 1')

        super().__init__()
        # 0=RandomPolicy, 1=1st main policy snapshot,
        # 2=2nd main policy snapshot, etc..
        self.current_opponent = 0
        self.win_rate_threshold = win_rate_threshold

        # windowed game results
        self.window = deque[Summary](maxlen=episode_window)

        # overall metrics
        self.overall_win_rate = Percent.new()
        self.overall_color_balance = Percent.new()
        self.overall_color_results = defaultdict[Color, Percent](Percent.new)
        self.overall_player_results = defaultdict[str, Percent](Percent.new)

    def on_train_result(
        self,
        *,
        algorithm: Algorithm | None,
        result: dict[str, Any],
        **kwargs: dict[str, Any],
    ) -> None:
        if algorithm is None:
            raise ValueError('No algorithm provided')

        # calculate game stats
        main_policy_id = 'main_0'
        opponents = set()
        episode_win_rate = Percent.new()
        episode_color_balance = Percent.new()
        window_win_rate = Percent.new()
        window_color_balance = Percent.new()
        window_color_results = defaultdict[Color, Percent](Percent.new)
        window_player_results = defaultdict[str, Percent](Percent.new)

        for episode in algorithm._episode_history:
            summary = next(
                Summary(player.opponent, policy_id, OPPONENT_REWARDS[reward])
                for (player, policy_id), reward in episode.agent_rewards.items()
                if policy_id != main_policy_id
            )
            win = summary.result is Result.WIN
            played_black = summary.player is Color.BLACK
            opponents.add(summary.opponent)

            # update episode metrics
            episode_win_rate.append(win)
            episode_color_balance.append(played_black)

            # update windowed metrics
            self.window.append(summary)

            # update overall metrics
            self.overall_win_rate.append(win)
            self.overall_color_balance.append(played_black)
            self.overall_color_results[summary.player].append(win)
            self.overall_player_results[summary.opponent].append(win)

        # update windowed metrics
        for summary in self.window:
            win = summary.result is Result.WIN
            played_black = summary.player is Color.BLACK
            window_win_rate.append(win)
            window_color_balance.append(played_black)
            window_color_results[summary.player].append(win)
            window_player_results[summary.opponent].append(win)

        # remove opponents no longer playing
        for opponent in self.overall_player_results.keys() - opponents:
            self.overall_player_results.pop(opponent)

        result['game_stats'] = {
            'batch': {
                'win_rate': float(episode_win_rate),
                'color_balance': float(episode_color_balance),
            },
            'window': {
                'win_rate': float(window_win_rate),
                'win_rate_by_color': {
                    color.name.lower(): float(win_rate)
                    for color, win_rate in window_color_results.items()
                },
                'win_rate_by_opponent': {
                    opponent: float(win_rate)
                    for opponent, win_rate in window_player_results.items()
                },
                'color_balance': float(window_color_balance),
            },
            'overall': {
                'win_rate': float(self.overall_win_rate),
                'win_rate_by_color': {
                    color.name.lower(): float(win_rate)
                    for color, win_rate in self.overall_color_results.items()
                },
                'win_rate_by_opponent': {
                    opponent: float(win_rate)
                    for opponent, win_rate in self.overall_player_results.items()
                },
                'color_balance': float(self.overall_color_balance),
            },
        }

        win_rates_exceed_threshold = all(
            float(win_rate) > self.win_rate_threshold
            for win_rate in window_player_results.values()
        )
        sufficient_games_played = len(self.window) == self.window.maxlen

        # print(f'Iter={algorithm.iteration} win-rate={win_rate} -> ', end='')

        # If win rate is good -> Snapshot current policy and play against
        # it next, keeping the snapshot fixed and only improving the 'main'
        # policy.
        if win_rates_exceed_threshold and sufficient_games_played:
            self.window.clear()
            self.current_opponent += 1
            new_pol_id = f'main_{self.current_opponent}'
            # print(f'adding new opponent to the mix ({new_pol_id}).')

            # Re-define the mapping function, such that 'main' is forced
            # to play against any of the previously played policies
            # (excluding 'random').
            def policy_mapping_fn(
                agent_id: AgentID,
                episode: Episode,
                worker: RolloutWorker,
                **kwargs: dict[str, Any],
            ) -> PolicyID:
                # agent_id = [0|1] -> policy depends on episode ID
                # This way, we make sure that both policies sometimes play
                # (start player) and sometimes agent1 (player to move 2nd).
                policy_id = np.random.choice(list(range(1, self.current_opponent + 1)))
                return (
                    main_policy_id
                    if episode.episode_id % 2 == agent_id
                    else f'main_{policy_id}'
                )

            main_policy = algorithm.get_policy(main_policy_id)
            new_policy = algorithm.add_policy(
                policy_id=new_pol_id,
                policy_cls=type(main_policy),
                policy_mapping_fn=policy_mapping_fn,
            )

            # Set the weights of the new policy to the main policy.
            # We'll keep training the main policy, whereas `new_pol_id` will
            # remain fixed.
            main_state = main_policy.get_state()
            new_policy.set_state(main_state)
            # We need to sync the just copied local weights (from main policy)
            # to all the remote workers as well.
            algorithm.workers.sync_weights()
        # else:
        #     print('not good enough; will keep learning ...')

        # +2 = main + random
        result['league_size'] = self.current_opponent + 2

from __future__ import annotations

import re
from collections import defaultdict, deque
from functools import partial
from typing import Any

from pythello.player.rl.environment import DRAW_REWARD, WIN_REWARD


class WinRateCalculator:
    def __init__(self, episode_window: int = 1000) -> None:
        self._episode_window = episode_window
        self._history = defaultdict(partial(deque, maxlen=episode_window))

    def __call__(self, result: dict[str, Any]) -> None:
        # If no evaluation results -> Use hist data gathered for training.
        if 'evaluation' in result:
            hist_stats = result['evaluation']['hist_stats']
        else:
            hist_stats = result['hist_stats']

        result['game_results'] = {}

        for policy_id, rewards in hist_stats.items():
            mo = re.match('^policy_(.+)_reward$', policy_id)

            if mo is None:
                continue

            policy_id = mo.group(1)
            episode_wins = [reward == WIN_REWARD for reward in rewards]
            episode_draws = [reward == DRAW_REWARD for reward in rewards]
            policy_history = self._history[policy_id]
            policy_history.extend(episode_wins)

            result['game_results'][policy_id] = {
                'win_rate': sum(policy_history) / len(policy_history),
                'episode_win_rate': sum(episode_wins) / len(episode_wins),
                'episode_draw_rate': sum(episode_draws) / len(episode_draws),
            }

    def clear(self) -> None:
        self._history.clear()

    def copy(self) -> WinRateCalculator:
        new = WinRateCalculator(self._episode_window)
        # new._history = self._history.copy()
        for policy, history in self._history.items():
            new._history[policy].extend(self._history[policy].copy())
        return new

    def history(self, policy_id: str) -> deque[bool]:
        return self._history[policy_id].copy()

    def is_full(self, policy_id: str) -> bool:
        return len(self._history[policy_id]) == self._episode_window

    def win_rate(self, policy_id: str) -> float:
        return sum(self._history[policy_id]) / len(self._history[policy_id])

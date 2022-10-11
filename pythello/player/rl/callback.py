from __future__ import annotations

import re
from collections import defaultdict, deque
from functools import partial
from typing import TYPE_CHECKING, Any

import numpy as np
from ray.rllib.algorithms.callbacks import DefaultCallbacks

from .environment import DRAW_REWARD, WIN_REWARD

if TYPE_CHECKING:
    from ray.rllib.algorithms import Algorithm
    from ray.rllib.evaluation import Episode, RolloutWorker
    from ray.rllib.utils.typing import AgentID, PolicyID


class SelfPlayCallback(DefaultCallbacks):
    def __init__(self, win_rate_threshold: float, episode_window: int = 1000) -> None:
        if not 0 <= win_rate_threshold <= 1:
            raise ValueError('Win rate threshold must be between 0 and 1')

        super().__init__()
        # 0=RandomPolicy, 1=1st main policy snapshot,
        # 2=2nd main policy snapshot, etc..
        self.current_opponent = 0
        self.win_rate_threshold = win_rate_threshold
        self.win_history = defaultdict(partial(deque, maxlen=episode_window))

    def on_train_result(
        self,
        *,
        algorithm: Algorithm | None,
        result: dict[str, Any],
        **kwargs: dict[str, Any],
    ) -> None:
        if algorithm is None:
            raise ValueError('No algorithm provided')

        # If no evaluation results -> Use hist data gathered for training.
        if 'evaluation' in result:
            hist_stats = result['evaluation']['hist_stats']
        else:
            hist_stats = result['hist_stats']

        # calculate game performance for each policy
        result['game_results'] = {}

        for key, rewards in hist_stats.items():
            # get policy ID
            match = re.match('^policy_(.+)_reward$', key)

            if match is None:
                continue

            policy_id = match.group(1)

            # update policy win rate
            episode_wins = [reward == WIN_REWARD for reward in rewards]
            episode_draws = [reward == DRAW_REWARD for reward in rewards]
            policy_win_history = self.win_history[policy_id]
            policy_win_history.extend(episode_wins)

            # populate policy game results
            result['game_results'][policy_id] = {
                'win_rate': sum(policy_win_history) / len(policy_win_history),
                'episode_win_rate': sum(episode_wins) / len(episode_wins),
                'episode_draw_rate': sum(episode_draws) / len(episode_draws),
            }

        main_policy_id = 'main_0'
        main_win_rate = result['game_results'][main_policy_id]['win_rate']
        main_win_history = self.win_history[main_policy_id]
        full_window = len(main_win_history) == main_win_history.maxlen

        # print(f'Iter={algorithm.iteration} win-rate={win_rate} -> ', end='')

        # If win rate is good -> Snapshot current policy and play against
        # it next, keeping the snapshot fixed and only improving the 'main'
        # policy.
        if main_win_rate > self.win_rate_threshold and full_window:
            self.win_history.clear()
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

            new_policy = algorithm.add_policy(
                policy_id=new_pol_id,
                policy_cls=type(algorithm.get_policy(main_policy_id)),
                policy_mapping_fn=policy_mapping_fn,
            )

            # Set the weights of the new policy to the main policy.
            # We'll keep training the main policy, whereas `new_pol_id` will
            # remain fixed.
            main_state = algorithm.get_policy(main_policy_id).get_state()
            new_policy.set_state(main_state)
            # We need to sync the just copied local weights (from main policy)
            # to all the remote workers as well.
            algorithm.workers.sync_weights()
        # else:
        #     print('not good enough; will keep learning ...')

        # +2 = main + random
        result['league_size'] = self.current_opponent + 2

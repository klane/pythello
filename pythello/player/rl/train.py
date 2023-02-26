from __future__ import annotations

# import os
import warnings
from functools import partial
from typing import TYPE_CHECKING, Any

import ray
from gym.spaces import Discrete
# from ray import air, tune
# from ray.rllib.agents.ppo import PPOTorchPolicy, PPOTrainer
# from ray.rllib.algorithms import ppo
# from ray.rllib.examples.policy.random_policy import RandomPolicy
from ray.air import CheckpointConfig, RunConfig
# from ray.rllib.algorithms.alpha_zero.models.custom_torch_models import DenseModel
# from ray.rllib.algorithms.callbacks import MultiCallbacks
from ray.rllib.policy.policy import PolicySpec
from ray.train.rl import RLTrainer
from ray.tune import Callback, CLIReporter, ExperimentAnalysis, Tuner
# from ray.tune.logger import pretty_print

from pythello.player.rl.callback import SelfPlayCallback
from pythello.player.rl.environment import Environment
from pythello.player.rl.model import ActionMaskModel
from pythello.player.rl.policy import RandomPolicy
# from pythello.player.rl.space import BoardObservationSpace


if TYPE_CHECKING:
    from ray.rllib.evaluation import Episode, RolloutWorker
    from ray.rllib.utils.typing import AgentID, PolicyID


def policy_mapping_fn(
    agent_id: AgentID, episode: Episode, worker: RolloutWorker, **kwargs: dict[str, Any]
) -> PolicyID:
    # agent_id = [0|1] -> policy depends on episode ID
    # This way, we make sure that both policies sometimes play agent0
    # (start player) and sometimes agent1 (player to move 2nd).
    return 'main_0' if episode.episode_id % 2 == agent_id else 'random'


def train_model(board_size: int) -> None:
    num_spaces = board_size**2
    empty_spaces = num_spaces - 4

    num_workers = 5
    # games_per_batch = 50
    # train_batch_size = games_per_batch * empty_spaces

    num_cpus = num_workers + 1
    local_mode = True
    log_to_driver = True

    # observation_space = BoardObservationSpace(board_size)

    config = {
        'env': Environment,
        'env_config': {
            'board_size': board_size,
            # 'observation_space': observation_space,
        },
        # 'observation_space': observation_space,
        # 'action_space': Discrete(num_spaces),
        'horizon': empty_spaces,
        'framework': 'torch',
        'model': {
            # 'custom_model': DenseModel,
            'custom_model': ActionMaskModel,
            'fcnet_hiddens': [num_spaces*2, num_spaces*2],
            'fcnet_activation': 'relu',
            # 'custom_model_config': {

            # },
        },

        # 'league_builder_config': {
        #     'type': CustomLeagueBuilder,
        # },

        'multiagent': {
            # Initial policy map: Random and PPO. This will be expanded
            # to more policy snapshots taken from main against which main
            # will then play (instead of random). This is done in the
            # custom callback defined above (`SelfPlayCallback`).
            'policies': {
                # Our main policy, we'd like to optimize.
                'main_0': PolicySpec(),
                # An initial random opponent to play against.
                'random': PolicySpec(policy_class=RandomPolicy),
            },
            # Assign agent 0 and 1 randomly to the main policy or
            # to the opponent (random at first). Make sure (via episode_id)
            # that main always plays against random (and not against
            # another main).
            'policy_mapping_fn': policy_mapping_fn,
            # Always just train the main policy.
            'policies_to_train': ['main_0'],
        },

        # 'callbacks': MultiCallbacks(
        #     [
        #         partial(WinRateCallback, episode_window=1000),
        #         partial(SelfPlayCallback, win_rate_threshold=0.8, episode_window=1000)
        #     ]
        # ),
        # 'callbacks': partial(WinRateCallback, episode_window=1000),
        'callbacks': partial(
            SelfPlayCallback,
            win_rate_threshold=0.8,
            episode_window=1000,
            # win_rate_decay=1.0,
            # win_rate_min=0.7,
        ),
        # 'callbacks': SelfPlayCallback(win_rate_threshold=0.8, episode_window=1000),

        'preprocessor_pref': None,
        'recreate_failed_workers': True,

        # 'rollout_fragment_length': empty_spaces,
        # 'train_batch_size': train_batch_size,

        'num_workers': num_workers,
        'num_envs_per_worker': 10,
        # 'num_envs_per_worker': train_batch_size // (empty_spaces * num_workers),

        # 'num_gpus': 0,
        'batch_mode': 'complete_episodes',

        # 'log_level': 'INFO',

        'lr': 0.0001,
        'kl_coeff': 0.0,
        'entropy_coeff': 0.01,
        'gamma': 0.99,
        'lambda': 0.95,
        'clip_param': 0.2,
        'vf_loss_coeff': 0.5,

        # 'num_sgd_iter': 50,
        # 'rollout_fragment_length': empty_spaces,
        # 'train_batch_size': empty_spaces * 100,

        # 'ranked_rewards': {
        #     'enable': True
        # }
    }

    # class MyCallback(Callback):
    #     def on_trial_result(self, iteration, trials, trial, result, **info):
    #         print(f"Got result: {result['metric']}")

    run_config = RunConfig(
        name='pythello',
        local_dir='./training_runs',
        log_to_file=True,
        verbose=1,
        # callbacks=[SelfPlayCallback2(win_rate_threshold=0.8, episode_window=1000)],
        stop={
            'training_iteration': 5000,
            # 'timesteps_total': 10000000,
            # 'episode_reward_mean': args.stop_reward,
        },
        checkpoint_config=CheckpointConfig(
            # num_to_keep=5,
            # checkpoint_score_attribute=,
            # checkpoint_score_order=,
            checkpoint_frequency=10,
            checkpoint_at_end=True,
        ),
        progress_reporter=CLIReporter(
            max_report_frequency=1,
            metric_columns={
                'training_iteration': 'iter',
                'time_total_s': 'time',
                'timesteps_total': 'ts',

                # 'episodes_this_iter': 'episodes',
                'policy_reward_mean/main_0': 'reward',

                'game_stats/batch/win_rate': 'batch win rate',
                # 'game_stats/batch/win_rate2': 'batch win rate2',
                # 'episode_win_rate': 'batch win rate',
                # 'custom_metrics/win_mean': 'win rate 2',
                # 'custom_metrics/win2_mean': 'win_rate3',

                # 'game_stats/batch/draw_rate': 'batch draw rate',
                # 'game_stats/batch/draw_rate2': 'batch draw rate2',
                # 'episode_draw_rate': 'batch draw rate',
                # 'custom_metrics/draw_mean': 'draw rate 2',
                # 'custom_metrics/draw2_mean': 'draw_rate3',

                'game_stats/window/win_rate': 'win rate',
                # 'win_rate': 'win rate',

                'game_stats/overall/color_balance': 'color balance',

                # 'threshold': 'threshold',
                'league_size': 'league size',
            },
            # sort_by_metric=True,
        ),
    )

    ray.init(num_cpus=num_cpus, local_mode=local_mode, log_to_driver=log_to_driver)

    trainer = RLTrainer(algorithm='PPO', config=config, run_config=run_config)
    # tuner = Tuner(trainer)
    # tuner = Tuner('PPO', param_space=config, run_config=run_config)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=DeprecationWarning)
        # results = tuner.fit()
        # tuner.fit()
        trainer.fit()

    # checkpoint_path = os.path.join(run_config.local_dir, run_config.name)
    # analysis = ExperimentAnalysis(experiment_checkpoint_path=checkpoint_path)

    # checkpoints = analysis.get_trial_checkpoints_paths(
    #     trial=analysis.get_best_trial('episode_reward_mean'),
    #     metric='episode_reward_mean'
    # )

    # last_checkpoint = analysis.get_last_checkpoint()

    # last_checkpoint = analysis.get_last_checkpoint(
    #     metric='episode_reward_mean', mode='max'
    # )

    ray.shutdown()

    # algo = ppo.PPO(config=config)

    # for _ in range(3):
    #     print(algo.train())

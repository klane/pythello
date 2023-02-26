from __future__ import annotations

import os
from functools import partial
from typing import TYPE_CHECKING, Any

# import ray
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.policy.policy import PolicySpec
from ray.tune import ExperimentAnalysis

from pythello.board import Board, Color
from pythello.game import Game
from pythello.player import AI
from pythello.player.rl.callback import SelfPlayCallback
from pythello.player.rl.environment import Environment
from pythello.player.rl.model import ActionMaskModel
from pythello.player.rl.player import RLPlayer
from pythello.player.rl.policy import RandomPolicy

if TYPE_CHECKING:
    from ray.rllib.evaluation import Episode, RolloutWorker
    from ray.rllib.utils.typing import AgentID, PolicyID


# def policy_mapping_fn(
#     agent_id: AgentID, episode: Episode, worker: RolloutWorker, **kwargs: dict[str, Any]
# ) -> PolicyID:
#     # agent_id = [0|1] -> policy depends on episode ID
#     # This way, we make sure that both policies sometimes play agent0
#     # (start player) and sometimes agent1 (player to move 2nd).
#     return 'main_0' if episode.episode_id % 2 == agent_id else 'random'


def run_model(board_size: int) -> None:
    num_spaces = board_size**2
    empty_spaces = num_spaces - 4

    # local_mode = True
    # log_to_driver = True
    # ray.init(num_cpus=6, local_mode=local_mode, log_to_driver=log_to_driver)

    # config = {
    #     'env': Environment,
    #     'env_config': {
    #         'board_size': board_size
    #     },
    #     'horizon': empty_spaces,
    #     'model': {
    #         # 'custom_model': DenseModel,
    #         'custom_model': ActionMaskModel,
    #         'fcnet_hiddens': [num_spaces*4, num_spaces*4],
    #         'fcnet_activation': 'relu',
    #         # 'custom_model_config': {

    #         # },
    #     },

    #     # 'league_builder_config': {
    #     #     'type': CustomLeagueBuilder,
    #     # },

    #     'multiagent': {
    #         # Initial policy map: Random and PPO. This will be expanded
    #         # to more policy snapshots taken from main against which main
    #         # will then play (instead of random). This is done in the
    #         # custom callback defined above (`SelfPlayCallback`).
    #         'policies': {
    #             # Our main policy, we'd like to optimize.
    #             'main_0': PolicySpec(),
    #             'main_1': PolicySpec(),
    #             'main_2': PolicySpec(),
    #             'main_3': PolicySpec(),
    #             'main_4': PolicySpec(),
    #             'main_5': PolicySpec(),
    #             'main_6': PolicySpec(),
    #             'main_7': PolicySpec(),
    #             # An initial random opponent to play against.
    #             'random': PolicySpec(policy_class=RandomPolicy),
    #         },
    #         # Assign agent 0 and 1 randomly to the main policy or
    #         # to the opponent (random at first). Make sure (via episode_id)
    #         # that main always plays against random (and not against
    #         # another main).
    #         # 'policy_mapping_fn': policy_mapping_fn,
    #         # # Always just train the main policy.
    #         # 'policies_to_train': ['main_0'],
    #     },

    #     # 'callbacks': MultiCallbacks(
    #     #     [
    #     #         partial(WinRateCallback, episode_window=1000),
    #     #         partial(SelfPlayCallback, win_rate_threshold=0.8, episode_window=1000)
    #     #     ]
    #     # ),
    #     # 'callbacks': partial(WinRateCallback, episode_window=1000),
    #     # 'callbacks': partial(
    #     #     SelfPlayCallback,
    #     #     win_rate_threshold=0.8,
    #     #     episode_window=1000,
    #     #     # win_rate_decay=1.0,
    #     #     # win_rate_min=0.7,
    #     # ),
    #     # 'callbacks': SelfPlayCallback(win_rate_threshold=0.8, episode_window=1000),
    #     'framework': 'torch',

    #     # 'num_workers': 5,
    #     # 'num_envs_per_worker': 10,
    #     # 'num_gpus': 0,
    #     # 'batch_mode': 'complete_episodes',

    #     # 'log_level': 'INFO',

    #     # 'lr': 0.0001,
    #     # 'kl_coeff': 0.0,
    #     # 'entropy_coeff': 0.01,
    #     # 'gamma': 0.99,
    #     # 'lambda': 0.95,
    #     # 'clip_param': 0.2,
    #     # 'vf_loss_coeff': 0.5,
    #     # 'num_sgd_iter': 50,
    #     # 'rollout_fragment_length': empty_spaces,
    #     # 'train_batch_size': empty_spaces * 100,

    #     # 'ranked_rewards': {
    #     #     'enable': True
    #     # }
    # }

    # checkpoint_path = os.path.join('./training_runs', 'pythello', 'experiment_state-2022-10-13_13-50-26.json')
    # checkpoint_path = os.path.join('training_runs', 'pythello', 'experiment_state-2022-10-26_07-19-48.json')
    checkpoint_path = os.path.join('training_runs', 'pythello', 'experiment_state-2022-10-30_08-50-46.json')
    analysis = ExperimentAnalysis(experiment_checkpoint_path=checkpoint_path)
    checkpoint = analysis.get_last_checkpoint()

    # checkpoint_path = './training_runs/pythello/PPO_Environment_528fe_00000_0_2022-10-11_11-55-49/checkpoint_001000/checkpoint-1000'
    # checkpoint_path = './training_runs/pythello/PPO_Environment_cea09_00000_0_2022-10-12_11-43-47/checkpoint_001000/checkpoint-1000'
    # checkpoint_path = './training_runs/pythello/AIRPPO_3f339_00000_0_2022-10-26_07-19-48/checkpoint_000100/checkpoint-100'

    board = Board(board_size)
    # game = Game(board)
    player = RLPlayer.from_checkpoint(checkpoint=checkpoint, num_workers=0, num_envs_per_worker=1)
    # player = RLPlayer(config=config, checkpoint_path=checkpoint_path)

    # action = player(game)

    # agent = PPOTrainer(config=config)
    # agent.restore('./training_runs/pythello/PPO_Environment_528fe_00000_0_2022-10-11_11-55-49/checkpoint_001000/checkpoint-1000')

    # env = Environment(config['env_config'])
    # action = agent.compute_single_action(env._current_observations(Color.BLACK), policy_id='main_0')

    # print(action, type(action))

    results = Game.series(board, AI.EDGE, player, 100, verbose=False)
    print(results)

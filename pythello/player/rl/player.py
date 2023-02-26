from __future__ import annotations

import os
import pickle
from typing import TYPE_CHECKING, Any

from ray.train.rl.rl_checkpoint import RL_CONFIG_FILE, RL_TRAINER_CLASS_FILE

if TYPE_CHECKING:
    from ray.air import Checkpoint
    from ray.train.rl import RLTrainer

    from pythello.board import Position
    from pythello.game import Game
    from pythello.player.rl.environment import Environment


class RLPlayer:
    def __init__(self, trainer: RLTrainer, env: Environment) -> None:
        # def __init__(self, checkpoint: Checkpoint) -> None:
        # checkpoint = RLCheckpoint.from_checkpoint(checkpoint)

        # with checkpoint.as_directory() as checkpoint_path:
        #     checkpoint_data_path = next(
        #         os.path.join(checkpoint_path, file)
        #         for file in os.listdir(checkpoint_path)
        #         if file.startswith('checkpoint') and not file.endswith('.tune_metadata')
        #     )
        #     trainer_class_path = os.path.join(checkpoint_path, RL_TRAINER_CLASS_FILE)
        #     config_path = os.path.join(checkpoint_path, RL_CONFIG_FILE)

        #     with open(trainer_class_path, 'rb') as fp:
        #         trainer_cls = pickle.load(fp)

        #     with open(config_path, 'rb') as fp:
        #         config = pickle.load(fp)

        #     config.get("evaluation_config", {}).pop("in_evaluation", None)
        #     config['num_workers'] = 0
        #     config['num_envs_per_worker'] = 1

        #     self.trainer = trainer_cls(config=config)  # , env=Environment)
        #     self.trainer.restore(checkpoint_data_path)

        # # self.env = Environment({'board_size': 8})
        # self.env = config['env'](config['env_config'])
        # # self.policy = trainer.get_policy('main_0')
        # # self.predictor = RLPredictor(policy=policy)

        # self.trainer, self.env = load_last_checkpoint(
        #     checkpoint_path, num_workers=0, num_envs_per_worker=1
        # )
        self.trainer = trainer
        self.env = env

    def __call__(self, game: Game) -> Position:
        obs = self.env.compute_observation(game.board, game.current_player.color)
        action = self.trainer.compute_single_action(obs, policy_id='main_0')
        # action, _, _ = self.policy.compute_single_action(obs)
        # action = self.predictor.predict(obs)
        return 1 << int(action)

    # def __init__(self, config: dict[str, Any], checkpoint_path: str) -> None:
    #     self.agent = PPOTrainer(config=config)
    #     self.agent.restore(checkpoint_path)
    #     self.env = self.agent.env_creator(config)
    #     # self.policy = self.agent.get_policy('main_0')

    # def __call__(self, game: Game) -> Position:
    #     obs = self.env.player_observation(game, game.current_player.color)
    #     # action, _, _ = self.policy.compute_single_action(obs)
    #     action = self.agent.compute_single_action(obs, policy_id='main_0')
    #     return 1 << int(action)

    @classmethod
    def from_checkpoint(
        cls, checkpoint: Checkpoint, **kwargs: dict[str, Any]
    ) -> RLPlayer:
        with checkpoint.as_directory() as checkpoint_path:
            checkpoint_data_path = next(
                os.path.join(checkpoint_path, file)
                for file in os.listdir(checkpoint_path)
                if file.startswith('checkpoint') and not file.endswith('.tune_metadata')
            )
            trainer_class_path = os.path.join(checkpoint_path, RL_TRAINER_CLASS_FILE)
            config_path = os.path.join(checkpoint_path, RL_CONFIG_FILE)

            with open(trainer_class_path, 'rb') as fp:
                trainer_cls = pickle.load(fp)

            with open(config_path, 'rb') as fp:
                config = pickle.load(fp)

            config.get('evaluation_config', {}).pop('in_evaluation', None)
            config.update(**kwargs)

            trainer = trainer_cls(config=config)
            trainer.restore(checkpoint_data_path)

            return cls(trainer=trainer, env=config['env'](config['env_config']))

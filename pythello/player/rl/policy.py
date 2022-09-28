from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

# from gym.spaces import Box
import numpy as np
import tree
from ray.rllib.models.modelv2 import _unpack_obs
from ray.rllib.policy.policy import Policy
from ray.rllib.policy.sample_batch import SampleBatch
from ray.rllib.utils.annotations import override

if TYPE_CHECKING:
    from ray.rllib.utils.typing import ModelWeights, TensorStructType, TensorType


class RandomPolicy(Policy):
    """Hand-coded policy that returns random actions."""

    @override(Policy)
    def init_view_requirements(self) -> None:
        # raise ValueError('view')
        super().init_view_requirements()
        # Disable for_training and action attributes for SampleBatch.INFOS column
        # since it can not be properly batched.
        vr = self.view_requirements[SampleBatch.INFOS]
        vr.used_for_training = False
        vr.used_for_compute_actions = False

    @override(Policy)
    def compute_actions(
        self,
        obs_batch: list[TensorStructType] | TensorStructType,
        state_batches: list[TensorType] | None = None,
        prev_action_batch: list[TensorStructType] | TensorStructType = None,
        prev_reward_batch: list[TensorStructType] | TensorStructType = None,
        **kwargs: dict[str, Any],
    ) -> tuple[TensorType, list[TensorType], dict[str, TensorType]]:
        # Working call to _unpack_obs
        unpacked_obs = _unpack_obs(
            np.array(obs_batch, dtype=np.float32),
            self.observation_space.original_space,
            tensorlib=np,
        )

        action_mask = unpacked_obs['action_mask']
        actions = [
            random.choice(np.where(action_mask[i, :] == 1)[0])
            for i in range(action_mask.shape[0])
        ]
        return actions, [], {}

    @override(Policy)
    def learn_on_batch(self, samples):
        """No learning."""
        raise ValueError('learn')
        return {}

    @override(Policy)
    def compute_log_likelihoods(
        self,
        actions,
        obs_batch,
        state_batches=None,
        prev_action_batch=None,
        prev_reward_batch=None,
    ):
        raise ValueError('log')
        action_mask = obs_batch[0, : self.action_space.n]
        return np.array([random.random()] * self.action_space.n) * action_mask

    @override(Policy)
    def get_weights(self) -> ModelWeights:
        """No weights to save."""
        # raise ValueError('get weights')
        return {}

    @override(Policy)
    def set_weights(self, weights: ModelWeights) -> None:
        """No weights to set."""
        # raise ValueError('set weights')
        pass

    @override(Policy)
    def _get_dummy_batch_from_view_requirements(self, batch_size: int = 1):
        raise ValueError('dummy')
        return SampleBatch(
            {
                SampleBatch.OBS: tree.map_structure(
                    lambda s: s[None], self.observation_space.sample()
                ),
            }
        )

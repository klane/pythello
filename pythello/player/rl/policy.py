from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

import numpy as np

from ray.rllib.models.modelv2 import _unpack_obs
from ray.rllib.policy.policy import Policy
from ray.rllib.utils.annotations import override

if TYPE_CHECKING:
    from ray.rllib.utils.typing import ModelWeights, TensorStructType, TensorType


class RandomPolicy(Policy):
    """Hand-coded policy that returns random actions."""

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
            obs=obs_batch,
            space=self.observation_space.original_space,
            tensorlib=np,
        )

        action_mask = unpacked_obs['action_mask']
        actions = [
            random.choice(np.where(action_mask[i, :] == 1)[0])
            for i in range(action_mask.shape[0])
        ]
        return actions, [], {}

    @override(Policy)
    def get_weights(self) -> ModelWeights:
        """No weights to save."""
        return {}

    @override(Policy)
    def set_weights(self, weights: ModelWeights) -> None:
        """No weights to set."""

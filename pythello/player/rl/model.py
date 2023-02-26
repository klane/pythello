from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch
from gym.spaces import Dict
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFC
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.utils.torch_utils import FLOAT_MIN
from torch import nn

if TYPE_CHECKING:
    from gym import Space
    from ray.rllib.utils.typing import ModelConfigDict, TensorType


class ActionMaskModel(TorchModelV2, nn.Module):
    """PyTorch version of above ActionMaskingModel."""

    def __init__(
        self,
        obs_space: Space,
        action_space: Space,
        num_outputs: int,
        model_config: ModelConfigDict,
        name: str,
        **kwargs: dict[str, Any],
    ) -> None:
        orig_space = getattr(obs_space, 'original_space', obs_space)

        if not isinstance(orig_space, Dict):
            raise ValueError('Observation space is not an instance of Dict')

        for key in ('action_mask', 'observation'):
            if key not in orig_space.spaces:
                raise ValueError(f'Observation space does not have a key "{key}"')

        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name, **kwargs
        )
        nn.Module.__init__(self)

        self.internal_model = TorchFC(
            orig_space['observation'],
            action_space,
            num_outputs,
            model_config,
            name + '_internal',
        )

    def forward(
        self,
        input_dict: dict[str, TensorType],
        state: list[TensorType],
        seq_lens: TensorType,
    ) -> tuple[TensorType, list[TensorType]]:
        # Compute the unmasked logits.
        logits, _ = self.internal_model({'obs': input_dict['obs']['observation']})

        # Extract the available actions tensor from the observation.
        action_mask = input_dict['obs']['action_mask']

        # Convert action_mask into a [0.0 || -inf]-type mask.
        inf_mask = torch.clamp(torch.log(action_mask), min=FLOAT_MIN)
        masked_logits = logits + inf_mask

        # Return masked logits.
        return masked_logits, state

    def value_function(self) -> TensorType:
        return self.internal_model.value_function()

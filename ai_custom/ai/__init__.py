import os
import json
import logging

from .numpy_model import NumPyModel

def load(config, agent, epoch):
    nn_path = config['ai']['path']
    metadata_path = os.path.splitext(nn_path)[0] + ".json"

    if os.path.exists(metadata_path):
        try:
            logging.info("[ai] loading %s", metadata_path)
            with open(metadata_path, "r") as f:
                json.load(f)
        except Exception as e:
            logging.warning("[ai] failed to load metadata: %s", e)

    logging.info("[ai] loading NumPy backend (no TensorFlow, no Stable-Baselines)")

    # USE THE EXISTING EPOCH OBJECT
    env = epoch
    env.last_reward = 0.0

    model = NumPyModel(env=env, nn_path=nn_path, gentle=True)
    return model


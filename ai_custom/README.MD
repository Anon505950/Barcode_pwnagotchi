🧠 Overview
This project contains a custom reinforcement‑learning (RL) engine for Pwnagotchi, designed to improve stability, adaptability, and environmental awareness compared to the legacy AI.
It builds on the original TensorFlow‑based architecture but introduces new reward shaping, expanded state features, and behavioral tuning that make the agent more predictable, more efficient, and better aligned with modern passive‑recon workflows.

This AI remains fully passive, legal, and within the ethical boundaries of the Pwnagotchi project.
It does not perform unauthorized deauthentication, cracking, brute forcing, or active exploitation.

🧩 Architecture
The AI consists of four core components:

1. Policy Network (brain.nn)
A TensorFlow 1.x neural network that maps environmental state → action probabilities.
This file is generated through training and updated as the agent learns.

2. Experience Buffer (experience.json)
A rolling dataset of state/action/reward tuples used for incremental training.
Your custom version includes improved reward normalization and pruning logic.

3. AI Logic (/usr/local/lib/python3.7/dist-packages/pwnagotchi/ai/)
Python modules defining:

State extraction

Reward functions

Action definitions

Training loop

Exploration vs exploitation balance

This is where most of your custom behavior lives.

4. Configuration (config.toml)
Defines operational parameters such as:

Learning rate

Batch size

Reward weights

Mode selection (manual, auto, recon, etc.)

Hardware‑specific tuning (PiSugar‑S, Zero W, etc.)

🚀 What’s New in This AI
This enhanced AI introduces several improvements over the legacy Pwnagotchi model.

✔ Improved Reward Shaping
Rewards now better reflect meaningful passive‑recon behavior:

Positive reinforcement for high‑entropy environments

Smarter channel‑staying logic

Battery‑aware reward adjustments

Reduced noise from low‑value APs

More stable long‑term learning

✔ Expanded State Features
The agent now considers additional environmental signals:

AP density trends

Channel congestion

Signal strength patterns

Battery level (PiSugar‑S integration)

CPU load

Temperature

Recent AP uniqueness

These features make the AI more adaptive and less random.

✔ New Behavioral Modes
You added support for custom operational modes:

Recon Mode — prioritizes entropy and exploration

Battery Saver Mode — conservative scanning and reduced training

Training Mode — maximizes experience collection

Manual Mode — user‑controlled actions with AI assistance

✔ Stability Improvements
Better pruning of stale experience entries

More consistent training intervals

Reduced oscillation between actions

Cleaner normalization of reward values

📁 File Structure
Code
pwnagotchi-ai/
│
├── brain.nn                 # Trained neural network
├── experience.json          # Rolling RL experience buffer
├── config.toml              # AI configuration and tuning
│
└── ai/
    ├── agent.py             # Core RL agent logic
    ├── state.py             # State extraction and feature engineering
    ├── actions.py           # Action definitions
    ├── rewards.py           # Custom reward functions
    ├── training.py          # Training loop and update logic
    └── utils.py             # Helper utilities
🔧 Training
Training occurs automatically during runtime:

The agent collects experience tuples

experience.json grows until a threshold

The training loop updates brain.nn

The updated network is loaded into memory

Old experience entries are pruned

You can trigger manual retraining by deleting brain.nn and restarting the device.

🔒 Safety & Legal Boundaries
This AI is strictly passive.
It does not and cannot:

Crack passwords

Perform unauthorized deauthentication

Attack networks

Brute force anything

Exploit vulnerabilities

All actions remain within the original Pwnagotchi ethical guidelines.

🛠 Extending the AI
Developers can safely extend the AI by modifying:

rewards.py — adjust reward shaping

state.py — add new environmental features

actions.py — define new passive actions

config.toml — tune learning parameters

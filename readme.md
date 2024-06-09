# Agent-centric autonomous vehicle controller simulator

The purpose of this simulator is to provide a visualisation of agent-centric vehicle models. It provides a global view with the agent-centric inputs shown as an excision. Top point of visualisation is `showGraphicView` in `mod/appControl/appControl.py`.

The simulator uses a logical controller provided as a scxml file. An interface for synthesising such a file with the help of TuLiP (The Temporal Logic Planning toolbox) is given in `mod/synthesise.py`. Example controllers are given in `mod/synthesis`.

The simulator can dump a history of a run as a text file.
The simulator as of now uses a model with a discrete location arena.

Example maps can be found in `maps/`.

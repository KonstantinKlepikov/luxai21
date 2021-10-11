# Luxai21 pipline

```bash
cd <bot folder>
```

## Example for `evol` folder

make game with cli (**uncorrect work** with logger)

```bash
sudo lux-ai-2021 main.py main.py --python=python3 --out=replays/replay.json
```

make game with python `python runner.py` or set full game options. You can use `agent_test.py` for test options

```bash
DEBUG=True PLAYER=agent.py OPPONENT=simple_agent python runner.py
```

You can start game from `runner.ipynb`

run visualisation

```bash
serve vis
```

make submission file (or `!sh make_sub.sh` for jupyter notebook)

```bash
sh make_sub.sh
```

make submit to kaggle (need `kaggle` library - use `requirements.txt` for install)

```bash
kaggle competitions submit -c lux-ai-2021 -f submissions/submission.tar.gz -m "submission"
```

## How it work

1. `bots` folder contains all scripts for build bot
2. `bots.utility` - genome generathors and constants
3. `bots.stements` - calculations of statements of tiles and map
4. `bots.performancies` - calculations of possible actions for every object in game
5. `bots.actions` - assignment of actions for every object
6. `bots.bot` - bot logic
7. `evol.py` is used for teach bot genome. Is learned on `agent_train.py`
8. `agent_test_evol.py` is used for test trained genome
9. `agent_test.py` is used in for bots with random generated genome
10. `agent.py` is used for submission

Pipline of every turn:

- statements is calculated
- performances is defined
- actions is defined
- final logic of bot is defined and list of actions is created
- next turn

Pipline of learning:

- define evolution learning constants in `evol.py`
- use defined alghoritms and methods or define owned
- start learning by run `python evol.py`
- look fo result in `bots_dump` folder

Project use [DEEP](https://deap.readthedocs.io/en/master/) framework for evolution learning

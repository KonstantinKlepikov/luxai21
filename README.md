# Luxai21 pipline

```sh
cd <folder>
```

## Example for `evol` folder

make game with cli (**uncorrect work** with logger)

```bash
sudo lux-ai-2021 main.py main.py --python=python3 --out=replays/replay.json
```

make game with python `python runner.py` or set full game options. You can use `agent_test.py` for test options

```bash
DEBUG=True PLAYER=agent_test.py OPPONENT=agent_random.py python runner.py
```

run visualisation

```bash
serve vis
```

make submission file

```bash
sh make_sub.sh
```

make submit to kaggle (need `kaggle` library - use `requirements.txt` for install)

```bash
kaggle competitions submit -c lux-ai-2021 -f submissions/submission.tar.gz -m "submission"
```

To learn bot use `evol.py` file by command like:

```bash
python evol.py
```

Be carefull - you need define correct parameters.

## How it work

1. `bots` folder contains all scripts for build bot
2. `bots.utility` - genome generathors and constants
3. `bots.statements` - calculations of statements tiles and map
4. `bots.missions` - calculations of possible actions for every object in game
5. `bots.bot` - bot logic
6. `bot.genutil.py` - genom constructor
7. `evol.py` it is used for teach bot genome
8. `agent_test.py` it is used for test trained genome
9. `agent_random.py` represents random generated genome
10. `agent_train.py` it is used for alghoritm learning
11. `agent.py` ii is used for submission (dont use for development)

Pipline of every turn:

- statements is calculated
- performances is defined
- actions is defined
- final logic of bot is defined and list of actions is created
- next turn

Pipline of learning:

- define evolution learning constants in `shared.env`
- use defined alghoritms and methods or define owned
- start learning by run `python evol.py`
- look fo result in `bots_dump` folder

Project is used [DEEP](https://deap.readthedocs.io/en/master/) framework for evolution learning

[List of available packages](https://github.com/Lux-AI-Challenge/Lux-Design-2021/blob/master/kaggle_engine/pythonpackages.txt) on kaggle env

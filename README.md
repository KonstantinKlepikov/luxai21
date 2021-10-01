# luxai21 pipline

```bash
cd <bot folder>
```

## Example for `simple` folder

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

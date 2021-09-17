# luxai21

You will need Node.js version 12 or above.

Open up the command line, and install the competition design with

`sudo npm install -g @lux-ai/2021-challenge@latest`

You may ignore any warnings that show up, those are harmless. To run a match from the command line (CLI), simply run

`sudo lux-ai-2021 path/to/botfile path/to/otherbotfile`

For a full list of commands from the CLI, run

`lux-ai-2021 --help`

## Resources

[Инструкция как пользоваться cli](https://github.com/Lux-AI-Challenge/Lux-Design-2021)

[Визуализация локально](https://github.com/Lux-AI-Challenge/Lux-Viewer-2021)

[Python Kit](https://github.com/Lux-AI-Challenge/Lux-Design-2021/tree/master/kits/python)

[kaggle-environments](https://github.com/Kaggle/kaggle-environments)

Kaggle Environments was created to evaluate episodes. While other libraries have set interface precedents (such as Open.ai Gym), the emphasis of this library focuses on:

- Episode evaluation (compared to training agents).
- Configurable environment/agent lifecycles.
- Simplified agent and environment creation.
- Cross language compatible/transpilable syntax/interfaces.

[web-hosted визуализатор матчей](https://2021vis.lux-ai.org/)

## Python kit

To get started, download the simple folder from this repository or via this [URL](https://github.com/Lux-AI-Challenge/Lux-Design-2021/raw/master/kits/python/simple/simple.tar.gz)

Then navigate to that folder via command line e.g. `cd simple`.

Your main code will go into `agent.py` and you can create and use files to help you as well. You should leave `main.py` and the entire lux subfolder alone. Read the `agent.py` file to get an idea of how a bot is programmed and a feel for the Python API.

Make sure your default python is python 3.7 or above. To check, run python -version. To then test run your bot, run

`sudo lux-ai-2021 main.py main.py --out=replay.json`

which should produce no errors. If your default python is not 3.7 or above, please install it and set it as your default python. If you can't set it as the default python (so python -version gives 3.7 or above), then you provide the command that is version 3.7 or above e.g.

`sudo lux-ai-2021 main.py main.py --python=python3 --out=replay.json`

## Submitting to Kaggle

Submissions need to be a `.tar.gz` bundle with `main.py` at the top level directory (not nested). To create a submission, cd simple then create the `.tar.gz` with `tar -czvf submission.tar.gz *`. Upload this under the My Submissions tab and you should be good to go! Your submission will start with a scheduled game vs itself to ensure everything is working.

## Visualisation local

To run the visualizer locally, first unzip the [release](https://github.com/Lux-AI-Challenge/Lux-Viewer-2021) and it should create a folder called dist. Then install the serve package via

`sudo npm i -g serve`

Then run `serve dist` (for this project from root folder run `serve vis`)

If you would like to view replays in higher quality, add "?scale=2" to the end of the visualizer url. For lower quality you can set as low as "?scale=1". Scale ranges from 1 to 3 with the default being 1.5.

e.g. [http://localhost:5000/?scale=2](http://localhost:5000/?scale=2) or [https://2021vis.lux-ai.org/?scale=2](https://2021vis.lux-ai.org/?scale=2)

## CLI Usage

### CLI General

The CLI tool has several options. For example, one option is the seed and to set a seed of 100 simply run

`lux-ai-2021 --seed=100 path/to/botfile path/to/otherbotfile`

which will run a match using seed 100.

You can tell the CLI tool whether to store the agent logs or match replays via `--storeLogs`, `--storeReplay`. Set these boolean options like so

```shell
# to set to true
lux-ai-2021 --statefulReplay
# to set to false
lux-ai-2021 --storeLogs=false
```

By default the tool will generate minimum, action-based, replays that are small in size and work in the visualizer but it does not have state information e.g. resources on the map in each turn. **To generate stateful replays**, set the `--statefulReplay` option to true. **To convert a action-based replay to a stateful one**, set the -`-convertToStateful` option to true and pass the file to convert.

Choose where the replay file is stored at by setting `--out=path/to/file.json`

You can also change the logging levels by setting `--loglevel=x` for number x from 0 to 4. The default is 2 which will print to terminal all game warnings and errors.

### CLI Leaderboard Evaluation

You can run your own local leaderboard / tournament to evaluate several bots at once via

`lux-ai-2021 --rankSystem="trueskill" --tournament path/to/agent1 path/to/agent2 path/to/agent3 path/to/agent4 ...`

This will run a leaderboard ranked by trueskill and print results as a table to your console. Agents are auto matched with opponents with similar ratings. Recommended to add --storeReplay=false --storeLogs=false as letting this run for a long time will generate a lot of replays and log files.

See `lux-ai-2021 --help` for more options.

## Summary pipline

from simple folder

- make game with cli: `sudo lux-ai-2021 main.py main.py --python=python3 --out=replays/replay.json` **uncorrect work**
- make game with python:`python runner.py` or set agents by `PLAYER=agent.py OPPONENT=simple_agent python runner.py`
- run visualisation: `serve vis`
- make submission file `sh make_sub.sh` or `!sh make_sub.sh` form jupyter notebook
- make submit to kaggle `kaggle competitions submit -c lux-ai-2021 -f submissions/submission.tar.gz -m "submission"`

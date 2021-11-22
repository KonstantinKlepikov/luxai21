#!/bin/bash

tar -czvf submissions/submission.tar.gz \
--exclude="*.gz" \
--exclude="*.ipynb" \
--exclude="*.sh" \
--exclude="*.log" \
--exclude=".ipynb_checkpoints" \
--exclude="__pycache__" \
--exclude="replays" \
--exclude="errorlogs" \
--exclude="vis" \
--exclude="img" \
--exclude="submissions" \
--exclude="runner.py" \
--exclude="agent_test.py" \
--exclude="agent_random.py" \
--exclude="agent_train.py" \
--exclude="npstatements.py" \
--exclude="tournament.py" \
--exclude="evol.py" \
--exclude="scoring.py" \
--exclude="_state_res.py" \
--exclude="_stat1_res.py" \
--exclude="bots_dump/hall_of_fame.json" \
--exclude="shared.env" \
*
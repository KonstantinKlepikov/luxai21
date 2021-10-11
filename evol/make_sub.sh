#!/bin/bash

tar -czf submissions/submission.tar.gz \
--exclude="*.gz" \
--exclude="*.ipynb" \
--exclude="*.sh" \
--exclude="errorlogs" \
--exclude="*.log" \
--exclude=".ipynb_checkpoints" \
--exclude="__pycache__" \
--exclude="replays" \
--exclude="vis" \
--exclude="submissions" \
--exclude="runner.py" \
--exclude="agent_test.py" \
--exclude="agent_test_evol.py" \
--exclude="agent_train.py" \
--exclude="npstatements.py" \
--exclude="tournament.py" \
--exclude="evol.py" \
*
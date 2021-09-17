#!/bin/bash

tar -czf submissions/submission.tar.gz --exclude="*.gz" --exclude="*.ipynb" --exclude="*.sh" --exclude="errorlogs" --exclude=".ipynb_checkpoints" --exclude="__pycache__" --exclude="replays" --exclude="vis" --exclude="submissions" --exclude="runner.py" --exclude="destribution.py" *
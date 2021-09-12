#!/bin/bash

tar -czf submission.tar.gz --exclude="*.gz" --exclude="*.ipynb" --exclude="*.sh" --exclude="errorlogs" --exclude=".ipynb_checkpoints" --exclude="__pycache__" --exclude="replays" *
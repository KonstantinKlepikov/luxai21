from kaggle_environments import make
from loguru import logger
import os, sys
import json


PLAYER = 'agent.py'
OPPONENT = 'simple_agent'
DEBUG = False


logger.remove()
logger.add(open(
    'errorlogs/run_test.log', 'w'),
    format='{time:HH:mm:ss} | {level} | {message}'
    )
logger.info('Start Logging...')


if 'PLAYER' in os.environ:
    PLAYER = os.environ['PLAYER']

if 'OPPONENT' in os.environ:
    OPPONENT = os.environ['OPPONENT']

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'True':
    DEBUG = True

logger.info(f'Is logged player: {PLAYER}, opponent: {OPPONENT} with debug: {DEBUG}')

env = make(
    'lux_ai_2021',
    configuration={'loglevel': 1, 'annotations': False},
    debug=DEBUG
    )

steps = env.run([PLAYER, OPPONENT])

replay = env.toJSON()
with open("replays/replay.json", "w") as f:
    json.dump(replay, f)

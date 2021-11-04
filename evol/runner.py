from logging import DEBUG
from kaggle_environments import make
from loguru import logger
import os, json
from dotenv import load_dotenv


load_dotenv(dotenv_path='shared.env')
PLAYER = os.environ['PLAYER']
OPPONENT = os.environ['OPPONENT']
DEBUG = os.environ['DEBUG']
if DEBUG == 'False': DEBUG == False
else: DEBUG == True

logger.remove()
logger.add(open(
    'errorlogs/run_test.log', 'w'),
    format='{time:HH:mm:ss} | {level} | {message}'
    )
logger.info('Start Logging...')
logger.info(f'Is logged player: {PLAYER}, opponent: {OPPONENT} with debug: {DEBUG}')

env = make(
    'lux_ai_2021',
    configuration={'loglevel': 1, 'annotations': False},
    debug=DEBUG
    )

steps = env.run([PLAYER, OPPONENT])

replay = env.toJSON()

PATH_TO = 'replays/replay.json'
if os.path.exists(PATH_TO):
    os.remove(PATH_TO)
with open(PATH_TO, "w") as f:
    json.dump(replay, f)

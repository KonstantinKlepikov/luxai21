from lux.game import Game
from bots.genutil import GenConstruct
import bots.bot as bot
from bots.statements import StorageStates
from loguru import logger
import json, datetime


logger.info('Start Logging agent_test.py...')

with open("bots_dump/best_bot.json", "r") as f:
    genome_list = json.load(f)
gen_const = GenConstruct()
# genome = gen_const.convert_day_genome(vector=genome_list)
genome = gen_const.convert_daily_genome(vector=genome_list)
game_state = None
storage = StorageStates()


def agent(observation, configuration):
    start = datetime.datetime.now()

    global game_state
    global genome
    global storage

    # Do not edit
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    # Bot code
    if game_state.turn == 0:
        logger.info('Agent is running!')
        # drop missions_state each game
        storage.missions_state = {}

    logger.info(f'-------------------> Start test turn {game_state.turn} <')
    logger.info(f'observation: {observation}')
    logger.info(f'missions_state: {storage.missions_state}')
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    actions = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        storage=storage,
        gen_const=gen_const
        )

    end = datetime.datetime.now()
    logger.info('time on this step: {}'.format(end - start))
    logger.info(f'-------------------> End test turn {game_state.turn} <')

    return actions

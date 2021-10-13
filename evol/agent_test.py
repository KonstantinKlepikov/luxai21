from lux.game import Game
from bots.utility import  GenConstruct
from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.bot import get_bot_actions
from loguru import logger
import json
import time


logger.info('Start Logging agent_test.py...')


with open("bots_dump/best_bot.json", "r") as f:
    genome_list = json.load(f)
gen_const = GenConstruct()
genome = gen_const.convert_genome(vector=genome_list)


game_state = None


def agent(observation, configuration):
    start = time.time()

    global game_state
    global genome

    # Do not edit #
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    # Bot code #
    if game_state.turn == 0:
        logger.info('Agent is running!')

    logger.info(f'Current turn: {game_state.turn}')
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    tiles_collection = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )

    states_collection = StatesCollectionsCollection(
        game_state=game_state,
        tiles_collection=tiles_collection
        )

    actions = get_bot_actions(
        genome=genome,
        tiles_collection=tiles_collection,
        states_collection=states_collection
        )

    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    logger.info('-'*20)

    return actions

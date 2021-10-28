from lux.game import Game
from bots.genutil import GenConstruct
from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.bot import get_bot_actions
import os, sys, json


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally

dir_path = os.path.dirname(__file__)
bot_genome_path = os.path.abspath(os.path.join(dir_path, "bots_dump/best_bot.json"))
with open(bot_genome_path, "r") as f:
    genome_list = json.load(f)
gen_const = GenConstruct()
genome = gen_const.convert_genome(vector=genome_list)

game_state = None


def agent(observation, configuration):

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

    return actions

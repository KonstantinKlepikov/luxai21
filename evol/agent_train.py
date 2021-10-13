from lux.game import Game
from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.bot import get_bot_actions
from loguru import logger


logger.info('Start Logging agent_train.py...')


game_state = None
genome = None


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
    actions = []

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

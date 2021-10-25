from lux.game import Game
from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.bot import get_bot_actions
from loguru import logger
from bots.utility import ALL_MORNINGS


logger.info('Start Logging agent_train.py...')


game_state = None
genome = None
game_eval = -1
intermediate = {}


def agent(observation, configuration):

    global game_state
    global genome
    global intermediate
    global game_eval

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
    
    # experimental intermediate scoring for fitness function
    # each morning we are scored count of player citytiles * 1000 + palyer units
    # then that numper is multipliced by serial number of the morning
    # for example, for 3 citytiles and 1 unit in turn 120 we have:
    # (3 * 10000 + 1) * 120/40 = 93000
    if game_state.turn == 0:
        game_eval += 1
        intermediate[game_eval] = 0
    
    if game_state.turn in ALL_MORNINGS:
        score = (len(tiles_collection.player_citytiles) * 10000 + \
            len(tiles_collection.player_units)) \
            * game_state.turn / 40
        intermediate[game_eval] =+ score
    # end scoring #

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

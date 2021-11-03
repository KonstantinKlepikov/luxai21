from lux.game import Game
from bots.statements import TilesCollection
from bots import bot
from loguru import logger
from bots.utility import ALL_MORNINGS


logger.info('Start Logging agent_train.py...')

game_state = None
genome = None
game_eval = -1
intermediate = {}
missions_state = {}


def agent(observation, configuration):

    global game_state
    global genome
    global intermediate
    global game_eval
    global missions_state

    # Do not edit
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    # Bot code
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    
    # experimental intermediate scoring for fitness function
    # each morning we are scored count of player citytiles * 1000 + palyer units
    # then that numper is multipliced by serial number of the morning
    # for example, for 3 citytiles and 1 unit in turn 120 we have:
    # (3 * 10000 + 1) * 120/40 = 93000
    tiles_collection = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )
    
    if game_state.turn == 0:
        # score additional scoring for each game
        game_eval += 1
        missions_state = {}
        intermediate[game_eval] = 0
        # drop missions_state each game
        missions_state = {}
    
    if game_state.turn in ALL_MORNINGS:
        score = (len(tiles_collection.player_citytiles) * 10000 + \
            len(tiles_collection.player_units)) \
            * game_state.turn / 40
        intermediate[game_eval] =+ score
    # end scoring

    actions, missions_state = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        missions_state=missions_state
        )

    return actions

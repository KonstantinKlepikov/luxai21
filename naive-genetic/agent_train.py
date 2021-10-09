from lux.game import Game
from performances import UnitPerformance, CityPerformance
from statements import TilesCollection, StatesCollectionsCollection
from bot import get_actions
from utility import init_logger

logger = init_logger(log_file='errorlogs/run.log')
logger.disabled = True

game_state = None
genome = None


def agent(observation, configuration):
    
    global game_state
    global genome

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    
    ### Bot code ###
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

    # get possible performances
    performances = []
    
    for unit in tiles_collection.player_units:
        act = UnitPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            unit=unit)
        performances.append(act.get_actions())

    for citytile in tiles_collection.player_citytiles:
        act = CityPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            citytile=citytile)
        performances.append(act.get_actions())
    
    actions = get_actions(
        genome=genome,
        tiles_collection=tiles_collection,
        states_collection=states_collection,
        logger=logger
        )
    
    return actions

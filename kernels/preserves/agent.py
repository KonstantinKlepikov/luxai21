# for kaggle-environments
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
from extractdata import get_turn_state, MapState
import sys
import time
from utility import init_logger, get_times_of_days


logger = init_logger(log_file='run.log')
logger.info(f'Start Logging...')

game_state = None
TIMES_OD_DAYS = get_times_of_days()


def agent(observation, configuration):
    start = time.time()
    
    global game_state

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
    
    turn_state = get_turn_state(
        game_state=game_state, 
        observation=observation, 
        times_of_days=TIMES_OD_DAYS,
        )    
    for key, val in turn_state._asdict().items():
        if key not in ['player', 'opponent', 'gamemap']:
            logger.info('{}: {}'.format(key, val))
  
    map_state = MapState(
        gamemap=turn_state.gamemap,
        width=turn_state.width,
        height=turn_state.height,
        player=turn_state.player,
        opponent=turn_state.opponent,
        )
    
    map_state.set_resources()    
    logger.info('bd_wood: {}'.format(map_state.bd_wood))
    logger.info('bd_coal: {}'.format(map_state.bd_coal))
    logger.info('bd_uranium: {}'.format(map_state.bd_uranium))
   
    map_state.set_unit_position()    
    logger.info('bd_unit: {}'.format(map_state.bd_unit))
  
    map_state.set_unit_properties()
    logger.info('unit_df: {}'.format(map_state.unit_df))
    
    map_state.set_city_properties()
    logger.info('city_df: {}'.format(map_state.city_df))
    
    map_state.set_resource_tiles_df(game_state=game_state)
    logger.info('resource_tiles_df: {}'.format(map_state.resource_tiles_df))
    
    map_state.set_team_df()
    logger.info('team_df: {}'.format(map_state.team_df))
    
    map_state.set_citytile_df()
    logger.info('citytile_df: {}'.format(map_state.citytile_df))

    end = time.time()
    logger.info('time on this step: {}'.format(end - start))

    return actions

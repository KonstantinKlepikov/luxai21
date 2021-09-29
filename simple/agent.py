from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import sys
import time
from utility import init_logger
from base_action import MapState, GameState, Storage, TileState


logger = init_logger(log_file='errorlogs/run.log')
logger.info(f'Start Logging...')

game_state = None
storaged_map_state = Storage()
storaged_game_state = Storage()


def agent(observation, configuration):
    start = time.time()
    
    global game_state
    global storaged_map_state
    global storaged_game_state

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
    
    if game_state.turn == 0:
        logger.info('Agent is running!')
        actions.append(annotate.circle(0, 0))
        
    current_game_state = GameState(game_state)
    current_game_state.set_state()
    storaged_game_state.set_storage(current_game_state.get_state())
    
    current_map_state = MapState(game_state)
    current_map_state.set_state()
    storaged_map_state.set_storage(current_map_state.get_state())
    
    units = game_state.players[0].units
    logger.info('Units: {}'.format(units))
    
    tilestate = TileState(game_state=game_state, x=units[0].pos.x, y=units[0].pos.y)
    logger.info('Is empty: {}'.format(tilestate.is_empty()))
    logger.info('Is worker: {}'.format(tilestate.is_worker))
    logger.info('Is city: {}'.format(tilestate.is_city))
    logger.info('Is road: {}'.format(tilestate.is_road))
    logger.info('Has resource: {}'.format(tilestate.has_resource))
    logger.info('Is wood: {}'.format(tilestate.is_wood()))
    logger.info('Is coal: {}'.format(tilestate.is_coal()))
    logger.info('Is uranium: {}'.format(tilestate.is_uranium()))
    logger.info('Is owned: {}'.format(tilestate.is_owned()))
    logger.info('Is owned by player: {}'.format(tilestate.is_owned_by_player()))
    logger.info('Is owned by opponent: {}'.format(tilestate.is_owned_by_opponent()))
    
    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    
    return actions

# logger.info('storaged_game_state: {}'.format(storaged_game_state.get_storage()))
# logger.info('storaged_map_state: {}'.format(storaged_map_state.get_storage()))

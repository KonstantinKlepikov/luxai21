from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import sys
import time
from utility import init_logger
from base_action import (
    MapState, GameState, Storage, TileState, Geometric, UnitActions
)


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

    unit = game_state.players[0].units[0]
    # unit = Position(0, 0)
    logger.info('Tile: {}'.format(unit.pos))

    tilestate = TileState(game_state=game_state, pos=unit.pos)
    logger.info('Is empty: {}'.format(tilestate.is_empty()))
    logger.info('Is worker: {}'.format(tilestate.is_worker))
    logger.info('Is cart: {}'.format(tilestate.is_cart))
    logger.info('Is city: {}'.format(tilestate.is_city))
    logger.info('Is road: {}'.format(tilestate.is_road))
    logger.info('Has resource: {}'.format(tilestate.has_resource))
    logger.info('Is wood: {}'.format(tilestate.is_wood()))
    logger.info('Is coal: {}'.format(tilestate.is_coal()))
    logger.info('Is uranium: {}'.format(tilestate.is_uranium()))
    logger.info('Is owned: {}'.format(tilestate.is_owned()))
    logger.info('Is owned by player: {}'.format(tilestate.is_owned_by_player()))
    logger.info('Is owned by opponent: {}'.format(tilestate.is_owned_by_opponent()))
    
    
    geometric = Geometric(pos=Position(0, 0))
    logger.info('Distance: {}'.format(geometric.get_distance(target_pos=Position(3, 3))))
    logger.info('Direction: {}'.format(geometric.get_direction(target_pos=Position(3, 3))))
    logger.info('Position by direction: {}'.format(geometric.get_position_by_direction(pos_dir='w')))
    logger.info('Agacent positions: {}'.format(geometric.get_ajacent_positions()))
    logger.info('Closest position: {}'.format(geometric.get_closest_pos(positions=[Position(1, 1), Position(5, 5)])))
    
    
    unit_actions = UnitActions(game_state=game_state, unit=unit)
    logger.info('Unit actions: {}'.format(unit_actions.set_actions()))
    
    
    logger.info('Turn is: {}'.format(game_state.turn))
    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    
    return actions

# logger.info('storaged_game_state: {}'.format(storaged_game_state.get_storage()))
# logger.info('storaged_map_state: {}'.format(storaged_map_state.get_storage()))

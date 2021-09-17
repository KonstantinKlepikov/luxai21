from lux.game import Game
from extractdata import get_turn_state, get_times_of_days, MapState
from utility import init_logger


logger = init_logger(log_file='run.log')
logger.info(f'Start Logging...')

game_state = None
TIMES_OD_DAYS = get_times_of_days()


def agent(observation, configuration):
    
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
  
    global mapsize
    global map_state
    
    mapsize = turn_state.width
    
    map_state = MapState(
        gamemap=turn_state.gamemap,
        width=turn_state.width,
        height=turn_state.height,
        player=turn_state.player,
        opponent=turn_state.opponent,
        )

    map_state.bd_wood[map_state.bd_wood > 0] = 1
    map_state.bd_coal[map_state.bd_coal > 0] = 1
    map_state.bd_uranium[map_state.bd_uranium > 0] = 1

    return actions

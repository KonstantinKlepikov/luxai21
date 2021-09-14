from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux.game_map import Cell
from lux.game_objects import Unit
from lux import annotate
import math
from collections import namedtuple


def get_times_of_days():
    
    day_list = list(range(0, 30))
    night_list = list(range(310, 360))
    mult = [0, 80, 160, 240]
    
    for i in list(range(70, 110)):
        day_list.extend([num + i for num in mult])
            
    for i in list(range(30, 70)):
        night_list.extend([num + i for num in mult])

    return {'day_list': day_list, 'night_list': night_list}


def get_turn_state(game_state, observation, times_of_days):
    
    TurnState = namedtuple('TurnState', ['step', 'time_of_day', 'player', 'opponent', 'width', 'height'])
    
    step = game_state.turn
    
    if step in times_of_days['day_list']:
        time_of_day = 'day'
    elif step in times_of_days['night_list']:
        time_of_day = 'night'
    
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height
    
    turn_state = TurnState(step, time_of_day, player, opponent, width, height)
    
    return turn_state

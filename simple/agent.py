# for kaggle-environments
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import extractdata
import sys

game_state = None
TIMES_OD_DAYS = extractdata.get_times_of_days()

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
        print(observation, file=sys.stderr)
    
    actions = []
    
    turn_state = extractdata.get_turn_state(
        game_state=game_state, 
        observation=observation, 
        times_of_days=TIMES_OD_DAYS
        )

    print(turn_state.step, file=sys.stderr)
    print(turn_state.time_of_day, file=sys.stderr)
    print(turn_state.player, file=sys.stderr)
    print(turn_state.opponent, file=sys.stderr)
    print(turn_state.width, file=sys.stderr)
    print(turn_state.height, file=sys.stderr)

    return actions

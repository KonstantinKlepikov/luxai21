# for kaggle-environments
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
from helper import (
    get_cells, move_unit, go_home, find_nearest_position
)
import extractdata
import sys

game_state = None
YIME_OD_DAY_LISTS = extractdata.get_times_of_day_lists()

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

    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height
    
    ##############################
    ### NOVEL CODE STARTS HERE ###
    ##############################

    # get all resource tiles
    researched_resource_cells = get_cells('researched resource', height, width, observation, game_state, player)
    citytile_cells = get_cells('player citytile', height, width, observation, game_state, player)

    # calculate number of citytiles
    num_citytiles = len(citytile_cells)

    # iterate over units
    for unit in player.units:
        if unit.is_worker() and unit.can_act():

            # if night and there are cities, return home:
            if game_state.turn % 40 > 30 and len(player.cities) > 0:
                go_home(unit, citytile_cells, actions)

            # if there is cargo space, find nearest resource and move towards it
            elif unit.get_cargo_space_left() > 0:
                nearest_resource_position = find_nearest_position(unit.pos, researched_resource_cells)
                move_unit(unit, nearest_resource_position, citytile_cells, actions)

            # if cargo is full
            else:
                # if there are no cities, build one if possible
                if len(player.cities) == 0:
                    if unit.can_build(game_state.map):
                        actions.append(unit.build_city)

                elif False: # some build condition here
                    if unit.can_build(game_state.map):
                        actions.append(unit.build_city)

                else:
                    nearest_citytile_position = find_nearest_position(unit.pos, citytile_cells)
                    move_unit(unit, nearest_citytile_position, citytile_cells, actions)
                
    # iterate through cities
    for k, city in player.cities.items():
        for citytile in city.citytiles:
            if citytile.can_act():

                # if there is space for more units, build a worker
                if num_citytiles > len(player.units):
                    actions.append(citytile.build_worker())
                
                # else research
                else:
                    actions.append(citytile.research())

    return actions

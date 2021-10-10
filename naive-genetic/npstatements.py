from lux.game import Game
from bots.utility import get_times_of_days
import numpy as np


day_or_night_calender = get_times_of_days()


class MapState:
    
    """Game state maps current map statement in 3-dimmensional array
    
    Array is orgnized as (x, y, feature vector)
    
    resource {True: 1, False: 0}
    type of resource {None: 0, 'wood': 1, 'coal': 2, 'uranium': 3}
    is cititile {True: 1, False: 0}
    can act {True: 1, False: 0}    
    """
    
    resources = {'wood': 1, 'coal': 2, 'uranium': 3}
    teams = {0: 1, 1: 2}
    feature_lenght = 21
    fmap = {
        'is_resource': 0,
        'resource_type': 1,
        'resource_amount': 2,
        'road': 3,
        'is_citytile': 4,
        'city_id': 5,
        'city_team': 6,
        'city_cooldown': 7,
        'city_can_act': 8,
        'city_fuel': 9,
        'city_light_upkeep': 10,
        'is_unit': 11,
        'unit_id': 12,
        'unit_team': 13,
        'unit_cooldown': 14,
        'unit_cargo_wood': 15,
        'unit_cargo-coal': 16,
        'unit_cargo_uranium': 17,
        'unit_cargo_space_left': 18,
        'unit_can_build': 19,
        'unit_can_act': 20,
    }


    def __init__(self, game_state: Game) -> None:
        
        self.game_state = game_state
        self.height = game_state.map.height
        self.width = game_state.map.width
        self.game_state_massive = None
        self.cityes = {**self.game_state.players[0].cities, **self.game_state.players[1].cities}
        self.units = self.game_state.players[0].units + self.game_state.players[1].units


    def set_state(self) -> None:
        
        self.game_state_massive = np.zeros([self.height, self.width, self.feature_lenght], np.float16)
        
        for h in range(self.height):
            for w in range(self.width):
                
                cell = self.game_state.map.get_cell(w, h)
                
                if cell.has_resource():
                    self.game_state_massive[w, h, self.fmap['is_resource']] = 1
                    self.game_state_massive[w, h, self.fmap['resource_type']] = self.resources[cell.resource.type]
                    self.game_state_massive[w, h, self.fmap['resource_amount']] = cell.resource.amount
                    
                if cell.road:
                    self.game_state_massive[w, h, self.fmap['road']] = cell.road
                    
                if cell.citytile:
                    self.game_state_massive[w, h, self.fmap['is_citytile']] = 1
                    self.game_state_massive[w, h, self.fmap['city_id']] = int(cell.citytile.cityid[2:])
                    self.game_state_massive[w, h, self.fmap['city_team']] = self.teams[cell.citytile.team]
                    self.game_state_massive[w, h, self.fmap['city_cooldown']] = cell.citytile.cooldown
                    
                    if cell.citytile.can_act():
                        self.game_state_massive[w, h, self.fmap['city_can_act']] = 1
                        
                    if self.cityes.get(cell.citytile.cityid, None):
                        self.game_state_massive[w, h, self.fmap['city_fuel']] = self.cityes[cell.citytile.cityid].fuel
                        self.game_state_massive[w, h, self.fmap['city_light_upkeep']] = self.cityes[cell.citytile.cityid].get_light_upkeep()

        for unit in self.units:
            w, h = unit.pos.x, unit.pos.y
            self.game_state_massive[w, h, self.fmap['is_unit']] = 1
            self.game_state_massive[w, h, self.fmap['unit_id']] = int(unit.id[2:])
            self.game_state_massive[w, h, self.fmap['unit_team']] = self.teams[unit.team]
            self.game_state_massive[w, h, self.fmap['unit_cooldown']] = unit.cooldown
            self.game_state_massive[w, h, self.fmap['unit_cargo_wood']] = unit.cargo.wood
            self.game_state_massive[w, h, self.fmap['unit_cargo-coal']] = unit.cargo.coal
            self.game_state_massive[w, h, self.fmap['unit_cargo_uranium']] = unit.cargo.uranium
            self.game_state_massive[w, h, self.fmap['unit_cargo_space_left']] = unit.get_cargo_space_left()
            self.game_state_massive[w, h, self.fmap['unit_can_build']] = unit.can_build(self.game_state.map)
            self.game_state_massive[w, h, self.fmap['unit_can_act']] = unit.can_act()

    
    def get_state(self) -> np.array:
       
        return self.game_state_massive


    def get_mapper(self) -> dict:
        
        return self.fmap


class GameState:
    """GameState maps current game statement to single vector
    """
    
    day_state = {'day': 0, 'night': 1}


    def __init__(self, game_state: Game) -> None:
        
        self.height = game_state.map.height
        self.width = game_state.map.width
        self.research_point_0 = game_state.players[0].research_points
        self.research_point_1 = game_state.players[1].research_points
        self.city_tiles_count_0 = game_state.players[0].city_tile_count
        self.city_tiles_count_1 = game_state.players[1].city_tile_count
        self.cities_count_0 = len(game_state.players[0].cities.keys())
        self.cities_count_1 = len(game_state.players[1].cities.keys())
        self.workers_count_0 = len(game_state.players[0].units)
        self.workers_count_1 = len(game_state.players[1].units)
        self.step = game_state.turn
        self.day_or_night = 1
        self.game_lenght = 360


    def set_state(self) -> None:

        if self.step in day_or_night_calender['day_list']:
            self.day_or_night = 1
        elif self.step in day_or_night_calender['night_list']:
            self.day_or_night = 0


    def get_state(self) -> np.array:
        
        n_array = np.array(list(self.__dict__.values()), np.int8)
        
        return n_array


    def get_mapper(self) -> dict:
        
        mapper = {key: val for val, key in enumerate(self.__dict__.keys())}
        
        return mapper


class Storage:
    """Set and get dict with all statement across the game
    
    Counter represents game turn
    """
    
    def __init__(self) -> None:
        self.storage = {}
        self.counter = 0
        
    def set_storage(self, massive: np.array) -> None:
        
        self.storage[self.counter] = massive
        self.counter += 1
        
    def get_storage(self) -> dict:
        
        return self.storage
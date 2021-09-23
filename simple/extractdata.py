from lux.game_map import Cell
from collections import namedtuple
import numpy as np
import pandas as pd


def get_turn_state(game_state, observation, times_of_days) -> namedtuple:
    
    TurnState = namedtuple('TurnState', ['step', 'time_of_day', 'player', 'opponent', 'width', 'height', 'gamemap'])
    
    step = game_state.turn
    
    if step in times_of_days['day_list']:
        time_of_day = 'day'
    elif step in times_of_days['night_list']:
        time_of_day = 'night'
    
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height
    
    gamemap = game_state.map.map
    
    turn_state = TurnState(step, time_of_day, player, opponent, width, height, gamemap)
    
    return turn_state


def find_resources(game_state) -> list:
    """
    this snippet finds all resources stored on the map and puts them into a list so we can search over them
    """
    resource_tiles: list[Cell] = []
    width, height = game_state.map_width, game_state.map_height
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)

    return resource_tiles


class MapState:

    resource_maps ={'wood':1,
                    'coal':2,
                    'uranium':3}

    def __init__(self, gamemap, width, height, player, opponent) -> None:
        self.height = width
        self.width = height
        self.bd = gamemap
        self.player = player
        self.opponent = opponent
        self.bd_res_type = np.zeros([height, width],np.int8)
        self.bd_wood = np.zeros([height, width],np.int16)
        self.bd_coal = np.zeros([height, width],np.int16)
        self.bd_uranium = np.zeros([height, width],np.int16)
        self.bd_res_amount = np.zeros([height, width],np.int16)
        self.bd_cityid = np.full([height, width],-1, np.int8)
        self.bd_city_cooldown = np.full([height, width], -1, np.int8)
        self.bd_city_can_act =  np.full([height, width],-1, np.int8)
        self.bd_city =  np.full([height, width], -1, np.int8)
        self.bd_road = np.full([height, width], -1, np.float32)#upgrade per 0.5
        #self.bd_city_fuel = np.full([height, width], -1, np.float32)
        #self.bd_city_light_upkeep = np.full([height, width], -1, np.float32)

        self.bd_unit = np.full([height, width],-1, np.int8)


    def set_resources(self) -> None:
        
        for y in range(self.height):
            for x in range(self.width):
                if self.bd[y][x].has_resource():
                    self.bd_res_type[y][x] = self.resource_maps[self.bd[y][x].resource.type]
                    self.bd_res_amount[y][x] = self.bd[y][x].resource.amount
                    if self.bd[y][x].resource.type=='wood':
                        self.bd_wood[y][x] = self.bd[y][x].resource.amount
                    elif self.bd[y][x].resource.type=='coal':
                        self.bd_coal[y][x] = self.bd[y][x].resource.amount
                    elif self.bd[y][x].resource.type=='uranium':
                        self.bd_uranium[y][x] = self.bd[y][x].resource.amount
                        
                if self.bd[y][x].citytile is not None:
                    self.bd_cityid[y][x] = int(self.bd[y][x].citytile.cityid.split('_')[-1])#self.bd[y][x]citytile.cityid#
                    self.bd_city_cooldown[y][x] = self.bd[y][x].citytile.cooldown
                    self.bd_city_can_act[y][x] = self.bd[y][x].citytile.can_act()
                    self.bd_city[y][x] = self.bd[y][x].citytile.team
                    #try:
                    #    city = player.cities[bd[y][x].citytile.cityid]
                    #except:
                    #    city = opponent.cities[bd[y][x].citytile.cityid]
                    #bd_city_fuel[y][x] = city.fuel
                    #bd_city_light_upkeep[y][x] = city.light_upkeep
                self.bd_road[y][x]= self.bd[y][x].road


    def set_unit_position(self) -> None:
        
        for unit in self.player.units:
            self.bd_unit[unit.pos.y][unit.pos.x] = 0

        for unit in self.opponent.units:
            self.bd_unit[unit.pos.y][unit.pos.x] = 1
            
    
    def set_unit_properties(self) -> None:
        
        list_ = []

        for unit in self.player.units + self.opponent.units:
            list_.append([
                    unit.id,
                    unit.team,
                    unit.pos.x,
                    unit.pos.y,
                    'worker' if unit.is_worker() else 'cart',
                    unit.cooldown,
                    unit.cargo.wood,
                    unit.cargo.coal,
                    unit.cargo.uranium,
                    unit.get_cargo_space_left(),
                    unit.can_act(),
                    ])

        self.unit_df = pd.DataFrame(list_, columns=[
            'id','team','pos_x','pos_y','type','cooldown',
            'cargo.wood','cargo.coal','cargo.uranium',
            'cargo_space_left','can_act',
            ])


    def set_city_properties(self) -> None:

        list_ = []
        cities = dict(self.player.cities, **self.opponent.cities)
        for city_id in cities.keys():
            list_.append(
                [cities[city_id].cityid,
                cities[city_id].team,
                cities[city_id].fuel, 
                cities[city_id].get_light_upkeep(),])
            
        self.city_df = pd.DataFrame(list_, columns=['cityid','team','fuel','light_upkeep'])
        
        
    def set_resource_tiles_df(self, game_state) -> None:
        
        list_ = []
        resource_tiles = find_resources(game_state)
        for cell in resource_tiles:
            list_.append([
                cell.resource.type, 
                cell.resource.amount,
                cell.pos.x,
                cell.pos.y,
                ])

        self.resource_tiles_df = pd.DataFrame(list_, columns=['type','amount','pos_x','pos_y',])
        
        
    def set_team_df(self) -> None:
        
        list_ = []
        for team in [self.player, self.opponent]:
            list_.append(
                [team.team,
                team.city_tile_count,
                len(team.units),
                team.research_points,
                team.researched_coal(),
                team.researched_uranium(),
                ])
            
        self.team_df = pd.DataFrame(list_, columns=[
            'team','city_tile_count', 'city_unit_count',
            'research_points','researched_coal','researched_uranium',
            ])
        
    def set_citytile_df(self) -> None:
        
        list_ = []
        cities = dict(self.player.cities, **self.opponent.cities)
        for city_id in cities.keys():
            for citytile in cities[city_id].citytiles:
                list_.append(
                    [citytile.cityid,
                    citytile.team,
                    citytile.pos.x,
                    citytile.pos.y,
                    citytile.cooldown,
                    citytile.can_act()])
        self.citytile_df = pd.DataFrame(list_, columns=['cityid','team','pos_x','pos_y','cooldown','can_act'])
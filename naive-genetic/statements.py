from lux.game import Game
from lux.game_objects import Player
from lux.game_map import Position
import numpy as np
from utility import get_times_of_days
from utility import init_logger
from utility import constants_dclass as cs

logger = init_logger(log_file='errorlogs/run.log')
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
    

class TilesMassives:
    """Get massives of tiles"""
    
    def __init__(self, game_state: Game, player: Player, opponent: Player) -> None:
        self.game_state = game_state
        self.player = player
        self.opponent = opponent
        self.__player_units = []
        self.__opponent_units = []
        self.__player_units_pos = []
        self.__opponent_units_pos = []
        self.__player_workers_pos = []
        self.__opponent_workers_pos = []
        self.__workers_pos = []
        self.__player_carts_pos = []
        self.__opponent_carts_pos = []
        self.__carts_pos = []
        self.__player_cities= []
        self.__opponent_cities = []
        self.__cities = []
        self.__player_citytiles = []
        self.__opponent_citytiles = []
        self.__citytiles = []
        self.__player_citytiles_pos = []
        self.__opponent_citytiles_pos = []
        self.__citytiles_pos = []
        self.__player_own = []
        self.__opponent_own = []
        self.__player_own_pos = []
        self.__opponent_own_pos = []
        self.__roads = []
        self.__roads_pos = []
        self.__resources = []
        self.__resources_pos = []
        self.__woods = []
        self.__coals = []
        self.__uraniums = []
        self.__woods_pos = []
        self.__coals_pos = []
        self.__uraniums_pos = []


    @property
    def player_units(self) -> list:
        if not self.__player_units:
            self.__player_units = self.player.units

        return self.__player_units


    @property
    def opponent_units(self) -> list:
        if not self.__opponent_units:
            self.__opponent_units = self.opponent.units
            
        return self.__opponent_units


    @property
    def player_units_pos(self) -> list:
        if not self.__player_units_pos:
            self.__player_units_pos = [unit.pos for unit in self.player_units]
        return self.__player_units_pos
    

    @property
    def player_units_pos(self) -> list:
        if not  self.__opponent_units_pos:
             self.__opponent_units_pos = [unit.pos for unit in self.opponent_units]
             
        return  self.__opponent_units_pos
    
    
    @property
    def player_workers_pos(self) -> list:
        if not self.__player_workers_pos:
            self.__player_workers_pos = [unit.pos for unit in self.player_units if unit.is_worker()]
            
        return self.__player_workers_pos


    @property
    def opponent_workers_pos(self) -> list:
        if not self.__opponent_workers_pos:
            self.__opponent_workers_pos = [unit.pos for unit in self.opponent_units if unit.is_worker()]
            
        return self.__opponent_workers_pos
    
    
    @property
    def workers_pos(self) -> list:
        if not self.__workers_pos:
            self.__workers_pos = self.player_workers_pos + self.opponent_workers_pos
            
        return self.__workers_pos
    
    
    @property
    def player_carts_pos(self) -> list:
        if not self.__player_carts_pos:
            self.__player_carts_pos= [unit.pos for unit in self.player_units if unit.is_cart()]
            
        return self.__player_carts_pos


    @property
    def opponent_carts_pos(self) -> list:
        if not self.__opponent_carts_pos:
            self.__opponent_carts_pos = [unit.pos for unit in self.opponent_units if unit.is_cart()]
            
        return self.__opponent_carts_pos
    

    @property
    def carts_pos(self) -> list:
        if not self.__carts_pos:
            self.__carts_pos = self.player_carts_pos + self.opponent_carts_pos
            
        return self.__carts_pos


    @property
    def player_cities(self) -> list:
        if not self.__player_cities:
            self.__player_cities = list(self.player.cities.values())

        return self.__player_cities


    @property
    def opponent_cities(self) -> list:
        if not self.__opponent_cities:
            self.__opponent_cities = list(self.opponent.cities.values())

        return self.__opponent_cities


    @property
    def cities(self) -> list:
        if not self.__cities:
            self.__cities = self.player_cities + self.opponent_cities

        return self.__cities
    

    @property
    def player_citytiles(self) -> list:
        if not self.__player_citytiles:
            _citytiles = []
            for city in self.player_cities:
                _citytiles = _citytiles + city.citytiles
            self.__player_citytiles = _citytiles

        return self.__player_citytiles


    @property
    def opponent_citytiles(self) -> list:
        if not self.__opponent_citytiles:
            _citytiles = []
            for city in self.opponent_cities:
                _citytiles = _citytiles + city.citytiles
            self.__opponent_citytiles = _citytiles

        return self.__opponent_citytiles


    @property
    def citytiles(self) -> list:
        if not self.__citytiles:
            self.__citytiles = self.player_citytiles + self.opponent_citytiles

        return self.__citytiles
    
    
    @property
    def player_citytiles_pos(self) -> list:
        if not self.__player_citytiles_pos:
            self.__player_citytiles_pos = [city.pos for city in self.player_citytiles]
            
        return self.__player_citytiles_pos


    @property
    def opponent_citytiles_pos(self) -> list:
        if not self.__opponent_citytiles_pos:
            self.__opponent_citytiles_pos = [city.pos for city in self.citytiles]
            
        return self.__opponent_citytiles_pos
    

    @property
    def citytiles_pos(self) -> list:
        if not self.__citytiles_pos:
            self.__citytiles_pos = self.player_citytiles_pos + self.opponent_citytiles_pos
            
        return self.__citytiles_pos
    

    @property
    def player_own(self) -> list:
        if not self.__player_own:
            self.__player_own = list(set(self.player_units + self.player_citytiles))
            
        return self.__player_own


    @property
    def opponent_own(self) -> list:
        if not self.__opponent_own:
            self.__opponent_own = list(set(self.opponent_units + self.opponent_citytiles))
            
        return self.__opponent_own
    
    
    @property
    def player_own_pos(self) -> list:
        if not self.__player_own_pos:
            self.__player_own_pos = [cell.pos for cell in self.player_own]
            
        return self.__player_own_pos


    @property
    def opponent_own_pos(self) -> list:
        if not self.__opponent_own_pos:
            self.__opponent_own_pos = [cell.pos for cell in self.opponent_own]
            
        return self.__opponent_own_pos


    @property
    def roads(self) -> list:
        if not self.__roads:
            self.__roads = [cell for cell in self.game_state.map if cell.road]
            
        return self.__roads


    @property
    def roads_pos(self) -> list:
        if not self.__roads_pos:
            self.__roads_pos = [cell.pos for cell in self.roads]
            
        return self.__roads_pos


    @property
    def resources(self) -> list:
        if not self.__resources:
            self.__resources = [cell for cell in self.game_state.map if cell.has_resource()]
        return self.__resources
    

    @property
    def resources_pos(self) -> list:
        if not self.__resources_pos:
            self.__resources_pos = [cell.pos for cell in self.resources]
        return self.__resources_pos
    
    
    @property
    def woods(self) -> list:
        if not self.__woods:
            self.__woods = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES_WOOD]
        return self.__woods


    @property
    def coals(self) -> list:
        if not self.__coals:
            self.__coals = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES_COAL]
        return self.__coals


    @property
    def uraniums(self) -> list:
        if not self.__uraniums:
            self.__uraniums = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES_URANIUM]
        return self.__uraniums


    @property
    def woods_pos(self) -> list:
        if not self.__woods_pos:
            self.__woods_pos = [cell.pos for cell in self.woods]
        return self.__woods_pos


    @property
    def coals_pos(self) -> list:
        if not self.__coals_pos:
            self.__coals_pos = [cell.pos for cell in self.coals]
        return self.__coals_pos


    @property
    def uraniums_pos(self) -> list:
        if not self.__uraniums_pos:
            self.__uraniums_pos = [cell.pos for cell in self.uraniums]
        return self.__uraniums_pos




class TileState:
    """Get tile statement
    """
    
    def __init__(self, game_state: Game, player: Player, opponent: Player, pos: Position) -> None:
        self.game_state = game_state
        self.cell = game_state.map.get_cell(pos.x, pos.y)
        self.player = player
        self.opponent = opponent
        self.__has_resource = False
        self.__is_road = False
        self.__is_city = False
        self.__is_worker = False
        self.__is_cart = False
        self.__resource_type = False
        self.__player_units = []
        self.__opponent_units = []
        self.__player_units_pos = []
        self.__worker_pos = []
        self.__cart_pos = []
        self.__tile_owner = None
        
    
    @property
    def _player_units(self) -> list:
        if not self.__player_units:
            self.__player_units = self.player.units

        return self.__player_units


    @property
    def _opponent_units(self) -> list:
        if not self.__opponent_units:
            self.__opponent_units = self.opponent.units
            
        return self.__opponent_units
    
    
    @property
    def _player_units_pos(self) -> list:
        if not self.__player_units_pos:
            self.__player_units_pos = [unit.pos for unit in self._player_units]
        return self.__player_units_pos
    
    
    @property
    def _workers_pos(self) -> list:
        if not self.__worker_pos:
            self.__worker_pos = [unit.pos for unit in self._player_units + self._opponent_units if unit.is_worker()]
            
        return self.__worker_pos
    
    
    @property
    def _cart_pos(self) -> list:
        if not self.__cart_pos:
            self.__cart_pos = [unit.pos for unit in self._player_units + self._opponent_units if unit.is_cart()]
            
        return self.__cart_pos


    @property
    def _tile_owner(self) -> int:
        if not self.__tile_owner:
            if self.is_city:
                self.__tile_owner = self.cell.citytile.team
            elif self.is_worker:
                if self.cell.pos in self.__player_units_pos:
                    self.__tile_owner = 0
                else:
                    self.__tile_owner = 1
                    
        return self.__tile_owner
    
    
    @property
    def _resource_type(self) -> bool:
        if not self.__resource_type and self.has_resource:
            self.__resource_type = self.cell.resource.type
            
        return self.__resource_type
    
    
    @property
    def is_city(self) -> bool:
        """Is tile city
        """
        if not self.__is_city and self.cell.citytile:
            self.__is_city = True
            
        return self.__is_city
    
    
    @property
    def is_worker(self) -> bool:
        """Is tile worker
        """
        if not self.__is_worker:
            if self.cell.pos in self._workers_pos:
                self.__is_worker = True
                
        return self.__is_worker
    
    
    @property
    def is_cart(self) -> bool:
        """Is tile worker
        """
        if not self.__is_cart:
            if self.cell.pos in self._cart_pos:
                self.__is_cart = True
                
        return self.__is_cart
    
    
    @property
    def has_resource(self) -> bool:
        """Has tile resource
        """
        if not self.__has_resource and self.cell.has_resource():
            self.__has_resource = True
            
        return self.__has_resource
    
    
    @property
    def is_road(self) -> bool:
        """Is tile Road
        """
        if not self.__is_road and self.cell.road:
            self.__is_road = True
            
        return self.__is_road


    def is_empty(self) -> True:
        """Is tile empty
        """
        if not self.has_resource and not self.is_road and not self.is_city and not self.is_worker:
            return True
    
    
    def is_wood(self) -> True:
        """Has tile wood resource
        """
        if self._resource_type == 'wood':
            return True


    def is_coal(self) -> True:
        """Has tile coal resource
        """
        if self._resource_type == 'coal':
            return True


    def is_uranium(self) -> True:
        """Has tile uranium resource
        """
        if self._resource_type == 'uranium':
            return True
        
        
    def is_owned(self) -> bool:
        """Is on tile something owned by somebody
        """
        return isinstance(self._tile_owner, int)
        
        
    def is_owned_by_player(self) -> True:
        """Is on tile something owned by player
        """
        if self._tile_owner == 0:
            return True
    
    
    def is_owned_by_opponent(self) -> True:
        """Is on tile something owned by opponent
        """
        if self._tile_owner == 1:
            return True
        
        
class TileState:
    """Get tile statement
    """
    
    def __init__(self, tile_massives: TilesMassives, pos: Position) -> None:
        self.tile_massives = tile_massives
        self.game_state = tile_massives.game_state
        self.cell = tile_massives.game_state.map.get_cell(pos.x, pos.y)
        self.__tile_owner = None
        self.__has_resource = False
        self.__is_road = False
        self.__is_city = False
        self.__is_worker = False
        self.__is_cart = False
        self.__resource_type = False
        

    @property
    def _tile_owner(self) -> int:
        if not self.__tile_owner:
            
            if (self.cell in self.tile_massives.player_citytiles) or (self.cell in self.tile_massives.player_citytiles)
            
            if self.is_city:
                self.__tile_owner = self.cell.citytile.team
            elif self.is_worker:
                if self.cell.pos in self.__player_units_pos:
                    self.__tile_owner = 0
                else:
                    self.__tile_owner = 1
                    
        return self.__tile_owner
    
    
    # @property
    # def _resource_type(self) -> bool:
    #     if not self.__resource_type and self.has_resource:
    #         self.__resource_type = self.cell.resource.type
            
    #     return self.__resource_type
    
    
    @property
    def is_city(self) -> bool:
        """Is tile city
        """
        if not self.__is_city and self.cell.citytile:
            self.__is_city = True
            
        return self.__is_city
    
    
    @property
    def is_worker(self) -> bool:
        """Is tile worker
        """
        if not self.__is_worker:
            if self.cell.pos in self._workers_pos:
                self.__is_worker = True
                
        return self.__is_worker
    
    
    @property
    def is_cart(self) -> bool:
        """Is tile worker
        """
        if not self.__is_cart:
            if self.cell.pos in self._cart_pos:
                self.__is_cart = True
                
        return self.__is_cart
    
    
    @property
    def has_resource(self) -> bool:
        """Has tile resource
        """
        if not self.__has_resource and self.cell.has_resource():
            self.__has_resource = True
            
        return self.__has_resource
    
    
    @property
    def is_road(self) -> bool:
        """Is tile Road
        """
        if not self.__is_road and self.cell.road:
            self.__is_road = True
            
        return self.__is_road


    def is_empty(self) -> True:
        """Is tile empty
        """
        if not self.has_resource and not self.is_road and not self.is_city and not self.is_worker:
            return True
    
    
    def is_wood(self) -> True:
        """Has tile wood resource
        """
        if self._resource_type == 'wood':
            return True


    def is_coal(self) -> True:
        """Has tile coal resource
        """
        if self._resource_type == 'coal':
            return True


    def is_uranium(self) -> True:
        """Has tile uranium resource
        """
        if self._resource_type == 'uranium':
            return True
        
        
    def is_owned(self) -> bool:
        """Is on tile something owned by somebody
        """
        return isinstance(self._tile_owner, int)
        
        
    def is_owned_by_player(self) -> True:
        """Is on tile something owned by player
        """
        if self._tile_owner == 0:
            return True
    
    
    def is_owned_by_opponent(self) -> True:
        """Is on tile something owned by opponent
        """
        if self._tile_owner == 1:
            return True
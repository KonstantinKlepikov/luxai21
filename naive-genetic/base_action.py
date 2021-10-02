from lux.game_objects import Unit, CityTile
from lux.game import Game
from lux.game_map import Position, Cell
from lux.game_constants import GAME_CONSTANTS as c
import numpy as np
from utility import get_times_of_days
import math
from typing import List
from utility import init_logger


logger = init_logger(log_file='errorlogs/utility.log')
logger.info(f'Start Logging...')


"""GAME_CONSTANTS
{'UNIT_TYPES': {'WORKER': 0, 'CART': 1}, 'RESOURCE_TYPES': {'WOOD': 'wood', 'COAL': 'coal', 'URANIUM': 'uranium'}, 'DIRECTIONS': {'NORTH': 'n', 'WEST': 'w', 'EAST': 'e', 'SOUTH': 's', 'CENTER': 'c'}, 'PARAMETERS': {'DAY_LENGTH': 30, 'NIGHT_LENGTH': 10, 'MAX_DAYS': 360, 'LIGHT_UPKEEP': {'CITY': 23, 'WORKER': 4, 'CART': 10}, 'WOOD_GROWTH_RATE': 1.025, 'MAX_WOOD_AMOUNT': 500, 'CITY_BUILD_COST': 100, 'CITY_ADJACENCY_BONUS': 5, 'RESOURCE_CAPACITY': {'WORKER': 100, 'CART': 2000}, 'WORKER_COLLECTION_RATE': {'WOOD': 20, 'COAL': 5, 'URANIUM': 2}, 'RESOURCE_TO_FUEL_RATE': {'WOOD': 1, 'COAL': 10, 'URANIUM': 40}, 'RESEARCH_REQUIREMENTS': {'COAL': 50, 'URANIUM': 200}, 'CITY_ACTION_COOLDOWN': 10, 'UNIT_ACTION_COOLDOWN': {'CART': 3, 'WORKER': 2}, 'MAX_ROAD': 6, 'MIN_ROAD': 0, 'CART_ROAD_DEVELOPMENT_RATE': 0.75, 'PILLAGE_RATE': 0.5}}
"""

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
    
    
class TileState:
    """Get tile statement
    """
    
    def __init__(self, game_state: Game, pos: Position) -> None:
        self.game_state = game_state
        self.cell = game_state.map.get_cell(pos.x, pos.y)
        self.__has_resource = False
        self.__is_road = False
        self.__is_city = False
        self.__is_worker = False
        self.__is_cart = False
        self.__resource_type = False
        self.__player_units = []
        self.__opponent_units = []
        self.__worker_pos = []
        self.__cart_pos = []
        self.__tile_owner = None
        
    
    @property
    def _player_units(self) -> list:
        if not self.__player_units:
            self.__player_units = self.game_state.players[0].units

        return self.__player_units


    @property
    def _opponent_units(self) -> list:
        if not self.__opponent_units:
            self.__opponent_units = self.game_state.players[1].units
            
        return self.__opponent_units
    
    
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


class Geometric:
    """Get geometric calculation acros map
    """
    
    def __init__(self, pos: Position) -> None:
        self.pos = pos


    def get_distance(self, target_pos: Position) -> float:
        """Get distance betwin positions
        Args:
            target_pos (Position): position object

        Returns:
            float: the Manhattan (rectilinear) distance 
        """
        
        return self.pos.distance_to(target_pos)
    
    
    def get_direction(self, target_pos: Position) -> str:
        """Get directin to target position
        Returns the direction that would move you closest to target_pos from this Position 
        if you took a single step. In particular, will return DIRECTIONS.CENTER if this Position 
        is equal to the target_pos. Note that this does not check for potential collisions with 
        other units but serves as a basic pathfinding method
        Args:
            target_pos (Position): position object

        Returns:
            str: DIRECTIONS prefix 
            s - south 
            n - nord
            w - west
            e - east
            c - center
        """
        
        return self.pos.direction_to(target_pos)
    
    
    def get_position_by_direction(self, pos_dir: str, eq: int = 1) -> Position:
        """Get position by direction"""
                
        return self.pos.translate(pos_dir, eq)
    
    
    def get_ajacent_positions(self) -> List[Position]:
        """Get ajacent positions

        Returns:
            list: List of ajacent objscts positions
        """        
        ajacent_pos = []
        for i in c['DIRECTIONS'].values():
            if i != 'c':
                ajacent_pos.append(self.pos.translate(i, 1))
            
        return ajacent_pos

    
    def get_closest_pos(self, positions: list) -> Position:
        """Get closest position

        Args:
            positions (list): list of Position objects

        Returns:
            Position: closest Position object
        """
        closest_dist = math.inf
        closest_pos = None
        for position in positions:
            dist = self.pos.distance_to(position)
            if dist < closest_dist:
                closest_dist = dist
                closest_pos = position
                
        return closest_pos


    def get_resource_tiles(self, game_state: Game) -> List[Position]:
        """Get list of resource tiles

        Args:
            game_state (Game): game state object

        Returns:
            List[Position]: list of positions objects
        """
        resource_tiles: list[Cell] = []
        for y in range(game_state.map_height):
            for x in range(game_state.map_width):
                cell = game_state.map.get_cell(x, y)
                if cell.has_resource():
                    resource_tiles.append(cell)
        return resource_tiles


class UnitPerformance:
    """Perform unit object with his posible actions
    """

    def __init__(self, game_state: Game, unit: Unit) -> None:
        self.unit = unit
        self.game_state = game_state
        self.actions = {}
        self.geometric = Geometric(unit.pos)
        self.__tile_states = []
        self.__current_tile_state = False
        
    
    @property 
    def _tile_states(self) -> List[TileState]:
        """Get list of statements of ajacent tiles

        Returns:
            list: list of statements
        """
        if not self.__tile_states:
            ajacent = self.geometric.get_ajacent_positions()
            for pos in ajacent:
                tile_state = TileState(game_state=self.game_state, pos=pos)
                self.__tile_states.append(tile_state)
        return self.__tile_states
    
    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: statements
        """
        if not self.__current_tile_state:
            self.__current_tile_state = TileState(game_state=self.game_state, pos=self.unit.pos)
        return self.__current_tile_state
    
    
    def _get_unit_type(self) -> str:
        """Get unit type

        Returns:
            str: CART or WORKER
        """
        if self.unit.is_cart():
            return 'CART'
        elif self.unit.is_worker():
            return 'WORKER'

       
    def _set_move(self) -> None:
        """Set move action
        """
        logger.info(f'Cargo space left {self.unit.get_cargo_space_left()}')
        if self.unit.get_cargo_space_left():
            self.actions['move_to_closest_resource'] = True
        else:
            self.actions['move_to_closest_citytile'] = True
        self.actions['move_random'] = True


    def _set_transfer(self) -> None:
        """Set transfere action
        """
        unit_type = self._get_unit_type()
        for state in self._tile_states:
            if state.is_owned_by_player() and (state.is_worker or state.is_cart):
                if not c['PARAMETERS']['RESOURCE_CAPACITY'][unit_type] - self.unit.get_cargo_space_left():
                    self.actions['transfer'] = True
                    break


    def _set_mine(self) -> None:
        """Set mine action
        
        Units cant mine from the cityes
        """
        if self.unit.get_cargo_space_left() and not self._current_tile_state.is_city:
            for state in self._tile_states:
                if state.is_wood():
                    self.actions['mine'] = True
                    break
                elif self.game_state.players[0].researched_coal() and state.is_coal():
                    self.actions['mine'] = True
                    break
                elif self.game_state.players[0].researched_uranium() and state.is_uranium():
                    self.actions['mine'] = True
                    break
            
    
    def _set_pillage(self) -> None:
        """Set pillage action
        
        Roads can be created only by carts. Roads dont have owners. 
        Citytiles has 6 road status by defoult
        """
        if self._current_tile_state.is_road and not self._current_tile_state.is_owned_by_player():
            self.actions['pillage'] = True


    def _set_build_city(self) -> None:
        """Set build city action
        """
        if self.unit.can_build(self.game_state.map):
            self.actions['build'] = True


    def get_actions(self) -> dict:
        """Set all possible actions

        Returns:
            dict: object and his posible actions
        """
        self.actions['obj'] = self.unit
        self.actions['u_pass'] = True
        if self.unit.can_act():
            self._set_move()
            self._set_transfer()
            if self.unit.is_worker():
                self._set_mine()
                self._set_pillage()
                self._set_build_city()
                
        return self.actions


class CityPerformance:
    """Perform citytile object with his posible actions
    """
    
    def __init__(self, game_state: Game, citytile: CityTile) -> None:
        self.game_state = game_state
        self.citytile = citytile
        self.__can_build = False
        self.actions = {}


    @property
    def can_build(self) -> bool:
        """Set citytile can build
        """
        if not self.__can_build:
            sum_units = len(self.game_state.players[0].units)
            sum_sityes = len(self.game_state.players[0].cities.keys())
            if sum_units - sum_sityes:
                self.__can_build = True
        return self.__can_build
    
    
    def _set_research(self) -> None:
        """Set citytile can research
        """
        if not self.game_state.players[0].researched_uranium():
            self.actions['research'] = True
    

    def _set_build(self) ->None:
        """Set citytile can build carts or workers
        
        City cant build units if citytiles == units, owned by player
        """
        if self.can_build:
            self.actions['build_worker'] = True
            self.actions['build_cart'] = True


    def get_actions(self) -> dict:
        """Set all possible actions

        Returns:
            dict: object and his posible actions
        """
        self.actions['obj'] = self.citytile
        self.actions['c_pass'] = True
        if self.citytile.can_act():
            self._set_research()
            self._set_build()
                
        return self.actions

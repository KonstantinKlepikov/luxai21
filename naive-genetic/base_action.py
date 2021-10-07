from lux.game_objects import Unit, CityTile
from lux.game_map import Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS as cs
import math
import random
from typing import List
from utility import init_logger
from statements import TileState, TilesCollection, StatesCollectionsCollection

RESOURCE_CAPACITY = Constants.RESOURCE_CAPACITY
DIRECTIONS = Constants.DIRECTIONS

logger = init_logger(log_file='errorlogs/run.log')

"""GAME_CONSTANTS
{'UNIT_TYPES': {'WORKER': 0, 'CART': 1}, 'RESOURCE_TYPES': {'WOOD': 'wood', 'COAL': 'coal', 'URANIUM': 'uranium'}, 'DIRECTIONS': {'NORTH': 'n', 'WEST': 'w', 'EAST': 'e', 'SOUTH': 's', 'CENTER': 'c'}, 'PARAMETERS': {'DAY_LENGTH': 30, 'NIGHT_LENGTH': 10, 'MAX_DAYS': 360, 'LIGHT_UPKEEP': {'CITY': 23, 'WORKER': 4, 'CART': 10}, 'WOOD_GROWTH_RATE': 1.025, 'MAX_WOOD_AMOUNT': 500, 'CITY_BUILD_COST': 100, 'CITY_ADJACENCY_BONUS': 5, 'RESOURCE_CAPACITY': {'WORKER': 100, 'CART': 2000}, 'WORKER_COLLECTION_RATE': {'WOOD': 20, 'COAL': 5, 'URANIUM': 2}, 'RESOURCE_TO_FUEL_RATE': {'WOOD': 1, 'COAL': 10, 'URANIUM': 40}, 'RESEARCH_REQUIREMENTS': {'COAL': 50, 'URANIUM': 200}, 'CITY_ACTION_COOLDOWN': 10, 'UNIT_ACTION_COOLDOWN': {'CART': 3, 'WORKER': 2}, 'MAX_ROAD': 6, 'MIN_ROAD': 0, 'CART_ROAD_DEVELOPMENT_RATE': 0.75, 'PILLAGE_RATE': 0.5}}
"""


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
    
    def get_ajacent_positions(self) -> List[Position]: # FIXME: out of range
        """Get ajacent positions

        Returns:
            list: List of ajacent objscts positions
        """
        ajacent_pos = []
        for i in cs['DIRECTIONS'].values():
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
            dist = self.pos.distance_to(position.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_pos = position
                
        return closest_pos.pos


class UnitPerformance:
    """Perform unit object with his posible actions
    """

    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collection: StatesCollectionsCollection, 
        unit: Unit
        ) -> None:
        self.unit = unit
        self.tiles_collection = tiles_collection
        self.states_collection = states_collection
        self.__current_tile_state = None
        self.__ajacent_tile_states = None
        self.actions = {}
        self.geometric = Geometric(unit.pos)
        
    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: statements
        """
        if self.__current_tile_state is None:
            self.__current_tile_state = self.states_collection.get_state(pos=self.unit.pos)

        return self.__current_tile_state

    @property 
    def _ajacent_tile_states(self) -> List[TileState]:
        """Get list of statements of ajacent tiles

        Returns:
            list: list of statements
        """
        if self.__ajacent_tile_states is None:
            ajacent = self.geometric.get_ajacent_positions() # TODO: move to tilestatements
            states = []
            for pos in ajacent:
                try: # FIXME: list index out of range (it is timless solution)
                    tile_state = self.states_collection.get_state(pos=pos)
                    states.append(tile_state)
                except IndexError:
                    continue
            self.__ajacent_tile_states = states
                
        return self.__ajacent_tile_states

    def _set_move(self) -> None:
        """Set move action
        """
        if self.unit.get_cargo_space_left():
            self.actions['move_to_closest_resource'] = True
        else:
            self.actions['move_to_closest_citytile'] = True
        self.actions['move_random'] = True


    def _set_transfer(self) -> None:
        """Set transfere action
        """
        for state in self._ajacent_tile_states: # TODO: move to tolestatements
            if state.is_owned_by_player:
                if state.is_worker and (RESOURCE_CAPACITY.WORKER - self.unit.get_cargo_space_left()):
                    self.actions['transfer'] = True
                    break
                elif state.is_cart and (RESOURCE_CAPACITY.CART - self.unit.get_cargo_space_left()):
                    self.actions['transfer'] = True
                    break

    def _set_mine(self) -> None:
        """Set mine action
        
        Units cant mine from the cityes
        """
        if self.unit.get_cargo_space_left() and not self._current_tile_state.is_city:
            for state in self._ajacent_tile_states:
                if state.is_wood:
                    self.actions['mine'] = True
                    break
                elif self.tiles_collection.player.researched_coal() and state.is_coal:
                    self.actions['mine'] = True
                    break
                elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
                    self.actions['mine'] = True
                    break
    
    def _set_pillage(self) -> None:
        """Set pillage action
        
        Roads can be created only by carts. Roads dont have owners. 
        Citytiles has 6 road status by defoult
        """
        if self._current_tile_state.is_road:
            self.actions['pillage'] = True

    def _set_build_city(self) -> None:
        """Set build city action
        """
        if self.unit.can_build(self.tiles_collection.game_state.map):
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
    
    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collection: StatesCollectionsCollection, 
        citytile: CityTile
        ) -> None:
        self.citytile = citytile
        self.tiles_collection = tiles_collection
        self.states_collection = states_collection
        self.__can_build = None
        self.actions = {}

    @property
    def _can_build(self) -> bool:
        """Set citytile can build
        """
        if self.__can_build is None:
            self.__can_build = bool(
                len(self.tiles_collection.player_units) - len(self.tiles_collection.player_cities)
                )
            
        return self.__can_build    
    
    def _set_research(self) -> None:
        """Set citytile can research
        """
        if not self.tiles_collection.player.researched_uranium():
            self.actions['research'] = True
    

    def _set_build(self) ->None:
        """Set citytile can build carts or workers
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
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


def get_action(tiles_collection: TilesCollection, obj_for_act: dict) -> str: #FIXME: refactoring
    global c
    if isinstance(obj_for_act['obj'], Unit):
        geo = Geometric(obj_for_act['obj'].pos)
        
        if obj_for_act['action'] == 'move_to_closest_resource':
            closest = geo.get_closest_pos(tiles_collection.resources)
            dir_to_closest = obj_for_act['obj'].pos.direction_to(closest)
            return obj_for_act['obj'].move(dir_to_closest)
        
        if obj_for_act['action'] == 'move_to_closest_citytile':
            closest = geo.get_closest_pos(tiles_collection.citytiles)
            dir_to_closest = obj_for_act['obj'].pos.direction_to(closest)
            return obj_for_act['obj'].move(dir_to_closest)

        if obj_for_act['action'] == 'move_random':
            seq = list(cs['DIRECTIONS'].values())
            return obj_for_act['obj'].move(random.choice(seq=seq))
        
        if obj_for_act['action'] == 'transfer': # TODO: ned to know resource for trasfere and dest
            return None

        if obj_for_act['action'] == 'mine':
            return None

        if obj_for_act['action'] == 'pillage':
            return obj_for_act['obj'].pillage()

        if obj_for_act['action'] == 'build':
            return obj_for_act['obj'].build_city()

        if obj_for_act['action'] == 'u_pass':
            return None

    if isinstance(obj_for_act['obj'], CityTile):
        if obj_for_act['action'] == 'research':
            return obj_for_act['obj'].research()

        if obj_for_act['action'] == 'build_cart':
            return obj_for_act['obj'].build_cart()

        if obj_for_act['action'] == 'build_worker':
            return obj_for_act['obj'].build_worker()

        if obj_for_act['action'] == 'c_pass':
            return None

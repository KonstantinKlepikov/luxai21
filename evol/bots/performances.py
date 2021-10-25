from lux.game_objects import Unit, CityTile
from lux.game_map import Position
from bots.utility import CONSTANTS as cs
from bots.statements import TileState, TilesCollection, StatesCollectionsCollection
import math
from typing import List
import os, sys


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


class Geometric:
    """Get geometric calculation across the map
    """
    
    def __init__(self, pos: Position) -> None:
        self.pos = pos

    def get_distance(self, target_pos: Position) -> float:
        """Get distance between positions
        Args:
            target_pos (Position): position object

        Returns:
            float: the Manhattan (rectilinear) distance 
        """
        
        return self.pos.distance_to(target_pos)    

    def get_direction(self, target_pos: Position) -> str:
        """Get direction to target position
        Returns the direction that would move you closest to target_pos from this Position 
        if you took a single step. In particular, will return DIRECTIONS.CENTER if this Position 
        is equal to the target_pos. Note that this does not check for potential collisions with 
        other units but serves as a basic pathfinding method
        Args:
            target_pos (Position): position object

        Returns:
            str: DIRECTIONS prefix 
            s - south 
            n - north
            w - west
            e - east
            c - center
        """
        return self.pos.direction_to(target_pos)

    def get_position_by_direction(self, pos_dir: str, eq: int = 1) -> Position:
        """Get position by direction"""
                
        return self.pos.translate(pos_dir, eq)
    
    def get_ajacent_positions(self) -> List[Position]: # FIXME: out of range
        """Get adjacent positions

        Returns:
            list: List of adjacent objects positions
        """
        ajacent_pos = []
        for i in cs.DIRECTIONS:
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
    """Perform unit object with his possible actions
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
        self.actions = {'obj': unit}
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
                try: # FIXME: list index out of range (it is temporal solution)
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
            self.actions['move_to_closest_resource'] = None
        else:
            self.actions['move_to_closest_citytile'] = None
        self.actions['move_random'] = None

    def _set_transfer(self) -> None:
        """Set transfer action
        """
        for state in self._ajacent_tile_states: # TODO: move to tolestatements
            if state.is_owned_by_player:
                if state.is_worker and (cs.RESOURCE_CAPACITY.WORKER - self.unit.get_cargo_space_left()):
                    self.actions['transfer'] = None
                    break
                elif state.is_cart and (cs.RESOURCE_CAPACITY.CART - self.unit.get_cargo_space_left()):
                    self.actions['transfer'] = None
                    break

    def _set_mine(self) -> None:
        """Set mine action
        
        Units cant mine from the cityes
        """
        if self.unit.get_cargo_space_left() and not self._current_tile_state.is_city:
            for state in self._ajacent_tile_states:
                if state.is_wood:
                    self.actions['mine'] = None
                    break
                elif self.tiles_collection.player.researched_coal() and state.is_coal:
                    self.actions['mine'] = None
                    break
                elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
                    self.actions['mine'] = None
                    break

    def _set_pillage(self) -> None:
        """Set pillage action
        
        Roads can be created only by carts. Roads dont have owners. 
        Citytiles has 6 road status by defoult
        """
        if self._current_tile_state.is_road:
            self.actions['pillage'] = None

    def _set_build_city(self) -> None:
        """Set build city action
        """
        if self.unit.can_build(self.tiles_collection.game_state.map):
            self.actions['build'] = None

    def get_actions(self) -> dict:
        """Set all possible actions

        Returns:
            dict: object and his posible actions
        """
        self.actions['u_pass'] = None
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
        self.actions = {'obj': citytile}

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
            self.actions['research'] = None

    def _set_build(self) -> None:
        """Set citytile can build carts or workers
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions['build_worker'] = None
            self.actions['build_cart'] = None

    def get_actions(self) -> dict:
        """Set all possible actions

        Returns:
            dict: object and his posible actions
        """
        self.actions['c_pass'] = None
        if self.citytile.can_act():
            self._set_research()
            self._set_build()

        return self.actions

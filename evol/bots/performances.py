from lux.game_objects import Unit, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
from bots.statements import TileState, TilesCollection, StatesCollectionsCollection
from typing import List, Dict, Union
import os, sys, math


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

    def get_closest_pos(self, positions: List[Union[Cell, CityTile, Unit]]) -> Position:
        """Get closest position

        Args:
            positions (list): list of objects

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


class Performance:
    
    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
        ) -> None:
        self.tiles_collection = tiles_collection
        self.states_collection = states_collection
        self.obj = obj_
        self.posible_actions = list(set([method for method in dir(Performance) if method.startswith('perform_')]))
        self.geo = Geometric(obj_.pos)
 
 
class UnitPerformance(Performance):
    
    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)
        self.actions:  Dict[str, Union[Unit, CityTile, str]]= {'obj': obj_}
        self.__current_tile_state = None
        self.__ajacent_tile_states = None

    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: statements
        """
        if self.__current_tile_state is None:
            self.__current_tile_state = self.states_collection.get_state(pos=self.obj.pos)

        return self.__current_tile_state
    
    @property 
    def _ajacent_tile_states(self) -> List[TileState]:
        """Get list of statements of ajacent tiles

        Returns:
            list: list of statements
        """
        if self.__ajacent_tile_states is None:
            tile_state = self.states_collection.get_state(pos=self.obj.pos)
            ajacent = tile_state.ajacent
            states = []
            for pos in ajacent:
                try: # FIXME: list index out of range (it is temporal solution)
                    tile_state = self.states_collection.get_state(pos=pos)
                    states.append(tile_state)
                except IndexError:
                    continue
            self.__ajacent_tile_states = states
 
        return self.__ajacent_tile_states

    def perform_move_to_city(self) -> None:
        """Perform move to closest city
        """
        if not self.obj.get_cargo_space_left():
            closest = self.geo.get_closest_pos(self.tiles_collection.citytiles)
            dir_to_closest = self.obj.pos.direction_to(closest)
            self.actions[self.perform_move_to_city.__name__] = self.obj.move(dir_to_closest)

    def perform_transfer(self) -> None: # TODO: need to know resource for transfer and destination
        """Perform transfer action
        """
        for state in self._ajacent_tile_states:
            if state.is_owned_by_player:
                if (state.is_worker and (cs.RESOURCE_CAPACITY.WORKER - self.obj.get_cargo_space_left())) or \
                    (state.is_cart and (cs.RESOURCE_CAPACITY.CART - self.obj.get_cargo_space_left())):
                    self.actions[self.perform_transfer.__name__] = None
                    break


class WorkerPerformance(UnitPerformance):
    """Perform worker object with his posible actions
    """

    def perform_move_to_resource(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            closest = self.geo.get_closest_pos(self.tiles_collection.resources)
            dir_to_closest = self.obj.pos.direction_to(closest)
            self.actions[self.perform_move_to_resource.__name__] = self.obj.move(dir_to_closest)

    def perform_pillage(self) -> None:
        """Perform pillage for worker
        """
        if self._current_tile_state.is_road:
            self.actions[self.perform_pillage.__name__] = self.obj.pillage()

    def perform_mine(self) -> None:
        """Performmine action
        
        Units cant mine from the cityes
        """
        if self.obj.get_cargo_space_left() and not self._current_tile_state.is_city:
            for state in self._ajacent_tile_states:
                if state.is_wood:
                    self.actions[self.perform_mine.__name__] = None
                    break
                elif self.tiles_collection.player.researched_coal() and state.is_coal:
                    self.actions[self.perform_mine.__name__] = None
                    break
                elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
                    self.actions[self.perform_mine.__name__] = None
                    break

    def perform_build_city(self) -> None:
        """Perform build city action
        """
        if self.obj.can_build(self.tiles_collection.game_state.map):
            self.actions[self.perform_build_city.__name__] = self.obj.build_city()


class CartPerformance(UnitPerformance):
    """Perform cart object with his posible actions
    """

    def perform_move_to_worker(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            closest = self.geo.get_closest_pos(self.tiles_collection.player_workers)
            dir_to_closest = self.obj.pos.direction_to(closest)
            self.actions[self.perform_move_to_worker.__name__] = self.obj.move(dir_to_closest)


class CityPerformance(Performance):
    """Perform citytile object with his posible actions
    """

    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)
        self.__can_build = None
        self.actions = {'obj': obj_}

    @property
    def _can_build(self) -> bool:
        """Set citytile can build
        """
        if self.__can_build is None:
            self.__can_build = bool(
                len(self.tiles_collection.player_units) - len(self.tiles_collection.player_cities)
                )
        return self.__can_build

    def perform_research(self) -> None:
        """Perform citytile research
        """
        if not self.tiles_collection.player.researched_uranium():
            self.actions[self.perform_research.__name__] = self.obj.research()

    def perform_build_worker(self) -> None:
        """Perform citytile build worker
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions[self.perform_build_worker.__name__] = self.obj.build_worker()

    def perform_build_cart(self) -> None:
        """Perform citytile build cart
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions[self.perform_build_cart.__name__] = self.obj.build_cart()


class PerformAndGetActions(Performance):
    
    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)
        self.geo = Geometric(obj_.pos)
        
    def get_actions(self) -> Dict[str, Union[Unit, CityTile, str]]:
        """Set all possible actions

        Returns:
            dict: object and his posible actions
        """
        perform = {'obj': self.obj}
        if self.obj.can_act():
            if isinstance(self.obj, Unit):
                if self.obj.is_worker():
                    perform = WorkerPerformance(
                        tiles_collection=self.tiles_collection,
                        states_collection=self.states_collection,
                        obj_=self.obj
                        )
                    perform.perform_move_to_city()
                    perform.perform_move_to_resource()
                    perform.perform_build_city()
                    perform.perform_mine()
                    perform.perform_transfer()
                    perform.perform_pillage()
                if self.obj.is_cart():
                    perform = CartPerformance(
                        tiles_collection=self.tiles_collection,
                        states_collection=self.states_collection,
                        obj_=self.obj
                        )
                    perform.perform_move_to_city()
                    perform.perform_move_to_worker()
                    perform.perform_transfer()
            if isinstance(self.obj, CityTile):
                    perform = CityPerformance(
                        tiles_collection=self.tiles_collection,
                        states_collection=self.states_collection,
                        obj_=self.obj
                        )
                    perform.perform_research()
                    perform.perform_build_cart()
                    perform.perform_build_worker()
                    
        return perform.actions

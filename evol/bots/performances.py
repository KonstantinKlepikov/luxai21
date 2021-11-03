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


class Performance:
    """Base class, provides constructor and methods
    for some calculations with object, that can act
    """
   
    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
                ) -> None:
        self.tiles_collection = tiles_collection
        self.states_collection = states_collection
        self.obj = obj_
        
    def _get_distance(self, target_pos: Position) -> float:
        """Get distance between positions
        Args:
            target_pos (Position): position object

        Returns:
            float: the Manhattan (rectilinear) distance 
        """
        
        return self.obj.pos.distance_to(target_pos)
    
    def _get_direction(self, target_pos: Position) -> str:
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
        return self.obj.pos.direction_to(target_pos)
    
    def _get_position_by_direction(self, pos_dir: str, eq: int = 1) -> Position:
        """Get position by direction"""
                
        return self.obj.pos.translate(pos_dir, eq)
    
    def _get_closest_pos(self, positions: List[Union[Cell, CityTile, Unit]]) -> Position:
        """Get closest position

        Args:
            positions (list): list of objects

        Returns:
            Position: closest Position object
        """
        closest_dist = math.inf
        closest_pos = None
        for position in positions:
            dist = self.obj.pos.distance_to(position.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_pos = position
        if closest_pos:     
            return closest_pos.pos
 
 
class UnitPerformance(Performance):
    """Performances for units of any type
    """

    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
                ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)
        self.actions:  Dict[str, Union[Unit, CityTile, str]] = {'obj': obj_}
        self.__current_tile_state = None
        self.__adjacent_tile_states = None

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
    def _adjacent_tile_states(self) -> List[TileState]:
        """Get list of statements of adjacent tiles

        Returns:
            list: list of statements
        """
        if self.__adjacent_tile_states is None:
            tile_state = self.states_collection.get_state(pos=self.obj.pos)
            adjacent = tile_state.adjacent
            states = []
            for pos in adjacent:
                tile_state = self.states_collection.get_state(pos=pos)
                states.append(tile_state)
            self.__adjacent_tile_states = states
 
        return self.__adjacent_tile_states

    def perform_move_to_city(self) -> None:
        """Perform move to closest city
        """
        if not self.obj.get_cargo_space_left():
            closest = self._get_closest_pos(self.tiles_collection.citytiles)
            if closest:
                dir_to_closest = self.obj.pos.direction_to(closest)
                self.actions[self.perform_move_to_city.__name__] = self.obj.move(dir_to_closest)

    def perform_transfer(self) -> None:  # TODO: need to know resource for transfer and destination
        """Perform transfer action
        """
        for state in self._adjacent_tile_states:
            if state.is_owned_by_player:
                if (state.is_worker and (cs.RESOURCE_CAPACITY.WORKER - self.obj.get_cargo_space_left())) or \
                   (state.is_cart and (cs.RESOURCE_CAPACITY.CART - self.obj.get_cargo_space_left())):
                    self.actions[self.perform_transfer.__name__] = None
                    break


class WorkerPerformance(UnitPerformance):
    """Perform worker object with his possible actions
    """

    def perform_move_to_resource(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            closest = self._get_closest_pos(self.tiles_collection.resources)
            if closest:
                dir_to_closest = self.obj.pos.direction_to(closest)
                self.actions[self.perform_move_to_resource.__name__] = self.obj.move(dir_to_closest)

    def perform_pillage(self) -> None:
        """Perform pillage for worker
        """
        if self._current_tile_state.is_road:
            self.actions[self.perform_pillage.__name__] = self.obj.pillage()

    def perform_mine(self) -> None:
        """Perform mine action
        
        Units cant mine from the cities
        """
        if self.obj.get_cargo_space_left() and not self._current_tile_state.is_city:
            for state in self._adjacent_tile_states:
                if state.is_wood:
                    self.actions[self.perform_mine.__name__] = None
                    break
                elif self.tiles_collection.player.researched_coal() and state.is_coal:
                    self.actions[self.perform_mine.__name__] = None
                    break
                elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
                    self.actions[self.perform_mine.__name__] = None
                    break

    def perform_build_city(self) -> None:  # TODO: perform to closest empty space and build
        """Perform build city action
        """
        if self.obj.can_build(self.tiles_collection.game_state.map):
            self.actions[self.perform_build_city.__name__] = self.obj.build_city()


class CartPerformance(UnitPerformance):
    """Perform cart object with his possible actions
    """

    def perform_move_to_worker(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            closest = self._get_closest_pos(self.tiles_collection.player_workers)
            if closest:
                dir_to_closest = self.obj.pos.direction_to(closest)
                self.actions[self.perform_move_to_worker.__name__] = self.obj.move(dir_to_closest)


class CityPerformance(Performance):
    """Perform citytile object with his possible actions
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
    """This class construct all possible performances and actions for all objects
    that can act
    """
    
    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
                ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)

    def get_actions(self) -> Dict[str, Union[Unit, CityTile, str]]:
        """Set all possible actions
        
        In this realisation we need use all methods of corresponded performance classes
        because on that is based genome

        Returns:
            dict: performed actions of object and actions
        """
        if self.obj.can_act():
            if isinstance(self.obj, Unit):
                logger.info('Im a unit')
                if self.obj.is_worker():
                    logger.info('Im a worker')
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
                    return perform.actions
                if self.obj.is_cart():
                    logger.info('Im a cart')
                    perform = CartPerformance(
                        tiles_collection=self.tiles_collection,
                        states_collection=self.states_collection,
                        obj_=self.obj
                        )
                    perform.perform_move_to_city()
                    perform.perform_move_to_worker()
                    perform.perform_transfer()
                    return perform.actions
            if isinstance(self.obj, CityTile):
                logger.info('Im a city')
                perform = CityPerformance(
                    tiles_collection=self.tiles_collection,
                    states_collection=self.states_collection,
                    obj_=self.obj
                    )
                perform.perform_research()
                perform.perform_build_cart()
                perform.perform_build_worker()
                return perform.actions
            logger.info('Im a nothing')
        logger.info('Im cant act')

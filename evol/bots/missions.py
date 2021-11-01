from lux.game_objects import Unit, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
from bots.statements import TileState, TilesCollection, StatesCollectionsCollection
from typing import List, Dict, Tuple, Union
import os, sys, math


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


class Mission:
    """Base class, provides constructhor and methods
    for some calculations with object, that can act
    """
   
    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collection: StatesCollectionsCollection,
        missions_state: Dict[str, str],
        obj_: Union[Unit, CityTile]
        ) -> None:
        self.tiles_collection = tiles_collection
        self.states_collection = states_collection
        self.missions_state: Dict[str, str] = missions_state
        self.actions:  Dict[str, Union[Unit, CityTile, str]]= {'obj': obj_}
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
 
 
class UnitMission(Mission):
    """Performances for units of any type
    """

    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        missions_state: Dict[str, str],
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, missions_state, obj_)
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

    def mission_move_to_city(self) -> None:
        """Move to closest city mission
        """
        if not self.obj.get_cargo_space_left():
            closest = self._get_closest_pos(self.tiles_collection.citytiles)
            if closest:
                dir_to_closest = self.obj.pos.direction_to(closest)
                self.actions[self.mission_move_to_city.__name__] = self.obj.move(dir_to_closest)
        if False: # TODO: when mission is complete
            self.missions_state.pop(self.obj.id, None)


class WorkerMission(UnitMission):
    """Worker object missions with his posible actions
    """

    def mission_move_to_resource(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            closest = self._get_closest_pos(self.tiles_collection.resources)
            if closest:
                dir_to_closest = self.obj.pos.direction_to(closest)
                self.actions[self.mission_move_to_resource.__name__] = self.obj.move(dir_to_closest)
        if False: # TODO: when mission is complete
            self.missions_state.pop(self.obj.id, None)

class CartMission(UnitMission):
    """Cart object missions with his posible actions
    """

    def mission_move_to_worker(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            closest = self._get_closest_pos(self.tiles_collection.player_workers)
            if closest:
                dir_to_closest = self.obj.pos.direction_to(closest)
                self.actions[self.mission_move_to_worker.__name__] = self.obj.move(dir_to_closest)
        if False: # TODO: when mission is complete
            self.missions_state.pop(self.obj.id, None)


class CityMission(Mission):
    """Citytile object moissions with his posible actions
    
    Citytile dont know his missions from previous turns
    """

    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        missions_state: Dict[str, str],
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, missions_state, obj_)
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

    def mission_research(self) -> None:
        """Citytile research mission
        """
        if not self.tiles_collection.player.researched_uranium():
            self.actions[self.mission_research.__name__] = self.obj.research()

    def mission_build_worker(self) -> None:
        """Citytile build worker mission
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions[self.mission_build_worker.__name__] = self.obj.build_worker()

    def mission_build_cart(self) -> None:
        """Citytile build cart mission
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions[self.mission_build_cart.__name__] = self.obj.build_cart()


class PerformMissionsAndActions(Mission):
    """This class construct all possible missions and actions for all objects
    that can act
    """
    
    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        missions_state: Dict[str, str],
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, missions_state, obj_)
        
    def _iterate_mission(
        self, 
        cls: Union[WorkerMission, CartMission, CityMission]
        ) -> Dict[str, Union[Unit, CityTile, str]]:
        perform = cls(
            tiles_collection=self.tiles_collection,
            states_collection=self.states_collection,
            missions_state=self.missions_state,
            obj_=self.obj
            )
        per = [method for method in dir(cls) if method.startswith('mission_')]
        for met in per:
            class_method = getattr(cls, met)
            class_method(perform)
            return perform.actions

    def _make_mission(
        self, 
        cls: Union[WorkerMission, CartMission, CityMission],
        mission: str
        ) -> Dict[str, Union[Unit, CityTile, str]]:
        perform = cls(
            tiles_collection=self.tiles_collection,
            states_collection=self.states_collection,
            missions_state=self.missions_state,
            obj_=self.obj
            )
        class_method = getattr(cls, mission)
        class_method(perform)
        return perform.actions

    def perform_missions_and_actions(self) -> Tuple[
        Dict[str, Union[Unit, CityTile, str]], 
        Dict[str, str]
        ]:
        """Set all possible actions
        
        In this realisation we need use all methods of corresponded performance classes
        because on that is based genom

        Returns:
            dict: performed actions of object and actions
        """
        if self.obj.can_act():
            if isinstance(self.obj, Unit):
                if self.obj.is_worker():
                    cls = WorkerMission
                if self.obj.is_cart():
                    cls = CartMission
            if isinstance(self.obj, CityTile):
                cls = CityMission
            if self.obj.id in self.missions_state.keys():
                logger.info('I have mission')
                return self._make_mission(cls=cls,
                    mission=self.missions_state[self.obj.id]), self.missions_state
            else:
                logger.info('No mission')
                return self._iterate_mission(cls=cls), self.missions_state

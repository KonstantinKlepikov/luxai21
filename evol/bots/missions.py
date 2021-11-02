from lux.game_objects import Unit, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
from bots.statements import TileState, TilesCollection, StatesCollectionsCollection
from typing import List, Dict, Tuple, Union
import os, sys, math, random


if os.path.exists("/kaggle"): # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger # log to file locally


class MissionInit:
    """Init some shared parameters
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
        self.missions_state = missions_state
        self.obj  = obj_ 


class Mission(MissionInit):
    """Base class, provides constructhor and methods
    for some calculations with object, that can act
    
        
    We add mission as key to self.action dict. As value we add
    action string or None if no any action needed in this mission on this turn
    
    We add new object id and his mission string to self.missions_state or remove
    ended mission
    
    self.check_again is used for check unit for new mission, when old is removed
    """
   
    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collection: StatesCollectionsCollection,
        missions_state: Dict[str, str],
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, missions_state, obj_)
        self.actions:  Dict[str, Union[Unit, CityTile, str]] = {'obj': obj_}
        self.check_again: Union[Unit, CityTile, str] = None
        self.tile_state: TileState = states_collection.get_state(obj_.pos)

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


class CityMission(Mission):
    """Citytile object missions with his posible actions
    
    Citytile can't add his missions to mission_state, because
    its missions is continue no longer than one turn
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

    @property
    def _can_build(self) -> bool:
        """Set citytile can build
        
        City cant build units if citytiles == units, owned by player
        """
        if self.__can_build is None:
            self.__can_build = bool(
                len(self.tiles_collection.player_units) - len(self.tiles_collection.player_cities)
                )
        return self.__can_build

    def mission_research(self) -> None:
        """Citytile research mission
        """
        name = self.mission_research.__name__
        if not self.tiles_collection.player.researched_uranium():
            self.actions[name] = self.obj.research()

    def mission_build_worker(self) -> None:
        """Citytile build worker mission
        """
        name = self.mission_build_worker.__name__
        if self._can_build:
            self.actions[name] = self.obj.build_worker()

    def mission_build_cart(self) -> None:
        """Citytile build cart mission
        """
        name = self.mission_build_cart.__name__
        if self._can_build:
            self.actions[name] = self.obj.build_cart()


class UnitMission(Mission):
    """Missions for units of any type
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
        self.__adjacent_tile_states = None

    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: current tile statement
        """
        if self.__current_tile_state is None:
            self.__current_tile_state = self.states_collection.get_state(pos=self.obj.pos)
        return self.__current_tile_state
    
    @property 
    def _adjacent_tile_states(self) -> List[TileState]:
        """Get list of statements of adjacent tiles

        Returns:
            list: list of statements of adjacent tiles
        """
        if self.__adjacent_tile_states is None:
            adjacent = self.tile_state.adjacent
            states = []
            for pos in adjacent:
                tile_state = self.states_collection.get_state(pos=pos)
                states.append(tile_state)
            self.__adjacent_tile_states = states
        return self.__adjacent_tile_states
    
    def _move_to_closest(self, name: str, tiles: List[Cell]) -> None:
        """Get move to closest tile of given type action

        Args:
            name (str): name of mission method
            tiles (List[Cell]): list of tiles for closest calculation
        """
        closest = self._get_closest_pos(tiles)
        if closest:
            dir_to_closest = self.obj.pos.direction_to(closest)
            self.actions[name] = self.obj.move(dir_to_closest)

    def _end_mission(self) -> None:
        """End mission, if it is in mission_state and 
        add object to check_again
        """
        self.missions_state.pop(self.obj.id, None)
        self.check_again = self.obj
        
    def _continue_mission(self, name: str) -> None:
        """Continue mission

        Args:
            name (str): name of mission method
        """
        self.missions_state[self.obj.id] = name

    def mission_drop_the_resources(self) -> None:
        """Move to closest city mission
        """
        name = self.mission_drop_the_resources.__name__
        if not self.obj.get_cargo_space_left():
            if self.tile_state.is_city:
                self._end_mission()
            else:
                closest = self._get_closest_pos(self.tiles_collection.citytiles)
                if closest:
                    self._move_to_closest(
                        name=name, 
                        tiles=self.tiles_collection.player_citytiles
                        )
                    self._continue_mission(name)

class WorkerMission(UnitMission):
    """Worker missions with his posible actions
    """

    def mission_main_resource(self) -> None:
        """Worker mission for mining resources
        """
        name = self.mission_main_resource.__name__
        if self.obj.get_cargo_space_left():
            if self.tile_state.is_city:
                self._move_to_closest(
                    name=name, 
                    tiles=self.tiles_collection.resources
                    )
            else:
                adjacence = self._adjacent_tile_states
                for state in adjacence:
                    if state.is_wood:
                        self.actions[name] = None
                        break
                    elif self.tiles_collection.player.researched_coal() and state.is_coal:
                        self.actions[name] = None
                        break
                    elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
                        self.actions[name] = None
                        break
                if self.actions.get(name, False) is False:
                    self._move_to_closest(
                        name=name, 
                        tiles=self.tiles_collection.resources
                        )
            self._continue_mission(name)
        else:
            self._end_mission()

    def mission_buld_the_city(self) -> None:
        """Worker mission to build a city
        """
        name = self.mission_buld_the_city.__name__
        if not self.obj.get_cargo_space_left():
            if self.obj.can_build:
                self.actions[name] = self.obj.build_city()
            else:
                seq = list(cs.DIRECTIONS)
                self.actions[name] = self.obj.move(random.choice(seq=seq))
            self._continue_mission(name)
        else:
            self._end_mission()


class CartMission(UnitMission):
    """Cart object missions with his posible actions
    """

    def mission_cart_harvest(self) -> None:
        """Perform move to closest resource
        """
        name = self.mission_cart_harvest.__name__
        if self.obj.get_cargo_space_left():
            self._move_to_closest(
                name=name, 
                tiles=self.tiles_collection.player_workers
                )
            self._continue_mission(name)
        else:
            self._end_mission()


class PerformMissionsAndActions(MissionInit):
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

    def _iterate_missions(
        self, 
        cls: Union[WorkerMission, CartMission, CityMission]
        ) -> Tuple[Dict[str, Union[Unit, CityTile, str]], Dict[str, str], Unit]:
        """Iterate missions for get all actions for object

        Args:
            cls (Union[WorkerMission, CartMission, CityMission]): mission class
            of object

        Returns:
            Tuple[Dict[str, Union[Unit, CityTile, str]], Dict[str, str], Unit]:
            actions. mission_state and check_again
        """
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
        return perform.actions, perform.missions_state, perform.check_again

    def _use_mission(
        self, 
        cls: Union[WorkerMission, CartMission, CityMission],
        mission: str
        ) -> Tuple[Dict[str, Union[Unit, CityTile, str]], Dict[str, str], Unit]:
        """Use mission for get all actions for object

        Args:
            cls (Union[WorkerMission, CartMission, CityMission]): mission class 
            of object
            mission (str): mission of object

        Returns:
            Tuple[Dict[str, Union[Unit, CityTile, str]], Dict[str, str], Unit]: 
            actions. mission_state and check_again
        """
        perform = cls(
            tiles_collection=self.tiles_collection,
            states_collection=self.states_collection,
            missions_state=self.missions_state,
            obj_=self.obj
            )
        class_method = getattr(cls, mission)
        class_method(perform)
        return perform.actions, perform.missions_state, perform.check_again

    def perform_missions_and_actions(self) -> Tuple[
        Dict[str, Union[Unit, CityTile, str]], 
        Dict[str, str],
        Unit
        ]:
        """Chack all missions, set actions and mission_statement

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
                return self._use_mission(cls=cls, mission=self.missions_state[self.obj.id])
            else:
                logger.info('No mission')
                return self._iterate_missions(cls=cls)

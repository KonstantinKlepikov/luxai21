from lux.game_objects import Unit, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
from bots.statements import (
    TileState, TilesCollection, StatesCollectionsCollection
)
from typing import List, Dict, Tuple, Union
import os, sys, math, random
from bots.utility import (
    GameActiveObjects, GameCellObjects, MissionState, 
    Missions, CheckAgain
)


if os.path.exists("/kaggle"): # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger # log to file locally


class Mission:
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
        states_collections: StatesCollectionsCollection,
        missions_state: MissionState,
        obj_: GameActiveObjects
        ) -> None:
        self.tiles_collection = tiles_collection
        self.states_collections = states_collections
        self.missions_state = missions_state
        self.obj  = obj_ 
        self.missions:  Missions = {'obj': obj_, 'missions': []}
        self.actions: List[str] = []
        self.check_again: CheckAgain = None

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
    
    def _get_closest_pos(self, positions: GameCellObjects) -> Position:
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
        states_collections: StatesCollectionsCollection,
        missions_state: MissionState,
        obj_: GameActiveObjects
        ) -> None:
        super().__init__(tiles_collection, states_collections, missions_state, obj_)
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
            logger.info('> citytile mission_research added')
            self.missions['missions'] = name
            
    def action_research(self) -> None:
        """Citytile research action
        """
        logger.info('> citytile action_research added')
        self.actions.append(self.obj.research())    

    def mission_build_worker(self) -> None:
        """Citytile build worker mission
        """
        name = self.mission_build_worker.__name__
        if self._can_build:
            logger.info('> citytile mission_build_worker added')
            self.missions['missions'] = name

    def action_build_worker(self) -> None:
        """Citytile build worker action
        """
        logger.info('> citytile action_build_worker added')
        self.actions.append(self.obj.build_worker()) 

    def mission_build_cart(self) -> None:
        """Citytile build cart mission
        """
        name = self.mission_build_cart.__name__
        if self._can_build:
            logger.info('> citytile mission_build_cart added')
            self.missions['missions'] = name
            
    def action_build_cart(self) -> None:
        """Citytile build cart action
        """
        logger.info('> citytile action_build_cart added')
        self.actions.append(self.obj.build_cart()) 


class UnitMission(Mission):
    """Missions for units of any type
    """

    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collections: StatesCollectionsCollection,
        missions_state: MissionState,
        obj_: GameActiveObjects
        ) -> None:
        super().__init__(tiles_collection, states_collections, missions_state, obj_)
        self.__adjacent_tile_states = None

    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: current tile statement
        """
        return self.states_collections.get_state(pos=self.obj.pos)
    
    @property 
    def _adjacent_tile_states(self) -> List[TileState]:
        """Get list of statements of adjacent tiles

        Returns:
            list: list of statements of adjacent tiles
        """
        if self.__adjacent_tile_states is None:
            adjacent = self._current_tile_state.adjacent
            states = []
            for pos in adjacent:
                tile_state = self.states_collections.get_state(pos=pos)
                states.append(tile_state)
            self.__adjacent_tile_states = states
        return self.__adjacent_tile_states
    
    def _move_to_closest_action(self, tiles: List[Cell]) -> None:
        """Get move to closest tile of given type action

        Args:
            name (str): name of mission method
            tiles (List[Cell]): list of tiles for closest calculation
        """
        closest = self._get_closest_pos(tiles)
        if closest:
            logger.info('> _move_to_closest: i calculate direction')
            dir_to_closest = self.obj.pos.direction_to(closest)
            self.actions.append(self.obj.move(dir_to_closest)) 

    def _end_mission(self) -> None:
        """End mission and add object to check_again
        """
        if self.obj.id in self.missions_state.keys():
            logger.info(f'> _end_mission: i try end mission. missions_state: {self.missions_state}')
            self.missions_state.pop(self.obj.id, None)
            logger.info(f'> _end_mission: i end mission. missions_state: {self.missions_state}')
            self.check_again = self.obj

    def mission_drop_the_resources(self) -> None:
        """Move to closest city mission
        """
        name = self.mission_drop_the_resources.__name__
        if not self.obj.get_cargo_space_left():
            logger.info('> mission_drop_the_resources: im fool')
            if self._current_tile_state.is_city:
                logger.info('> mission_drop_the_resources: im in city and drop this mission')
                self._end_mission()
            else:
                logger.info('> mission_drop_the_resources: im not in city')
                if self.tiles_collection.player_citytiles:
                    logger.info('> mission_drop_the_resources: citityles is exist')
                    self.missions['missions'] = name
        else:
            logger.info('> mission_drop_the_resources: im empty and drop this mission')
            self._end_mission()
    
    def action_drop_the_resources(self) -> None:
        """Move to closest city action
        """
        logger.info('> action_drop_the_resources: im here and go to closest city')
        self._move_to_closest_action(
            tiles=self.tiles_collection.player_citytiles
            )


class WorkerMission(UnitMission):
    """Worker missions with his posible actions
    """

    def mission_main_resource(self) -> None:
        """Worker mission for mining resources
        """
        name = self.mission_main_resource.__name__
        if not self.obj.get_cargo_space_left():
            logger.info('> mission_main_resource: im fool')
            self._end_mission()
        else:
            logger.info('> mission_main_resource: im empty')
            self.missions['missions'] = name
    
    def action_main_resource(self) -> None:
        """Worker action for mining resources
        """
        logger.info('> action_main_resource: im here')
        if self._current_tile_state.is_city:
            logger.info('> action_main_resource: im in city and go mine')
            self._move_to_closest_action(
                tiles=self.tiles_collection.resources
                )
        else:
            adjacence = self._adjacent_tile_states
            main_now = False # FIXME: no good resources to mine
            for state in adjacence: 
                if state.is_wood:
                    logger.info('> action_main_resource: i mine wood')
                    main_now = True
                    break
                elif self.tiles_collection.player.researched_coal() and state.is_coal:
                    logger.info('> action_main_resource: i mine coal')
                    main_now = True
                    break
                elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
                    logger.info('action_main_resource: i mine uranium')
                    main_now = True
                    break
            if not main_now:
                logger.info('> action_main_resource: im not in city and go mine')
                self._move_to_closest_action(
                    tiles=self.tiles_collection.resources
                    )

    def mission_buld_the_city(self) -> None:
        """Worker mission to build a city
        """
        name = self.mission_buld_the_city.__name__
        if self.obj.get_cargo_space_left():
            logger.info('> mission_buld_the_city: im empty and drop this mission')
            self._end_mission()
        else:
            logger.info('> mission_buld_the_city: im fool and can build city')
            self.missions['missions'] = name
                
    def action_buld_the_city(self) -> None:
        """Worker action to build a city
        """
        logger.info('> action_buld_the_city: im here')
        if self.obj.can_build(self.tiles_collection.game_state.map):
            logger.info('> action_buld_the_city: i build the city')
            self.actions.append(self.obj.build_city())
        else:
            logger.info('> action_buld_the_city: i move random')
            seq = list(cs.DIRECTIONS)
            self.actions.append(self.obj.move(random.choice(seq=seq)))


class CartMission(UnitMission):
    """Cart object missions with his posible actions
    """

    def mission_cart_harvest(self) -> None:
        """Cart mission move to closest resource
        """
        name = self.mission_cart_harvest.__name__
        if not self.obj.get_cargo_space_left():
            logger.info('> mission_cart_harvest: im empty')
            self._end_mission()
        else:
            logger.info('> mission_cart_harvest: im fool and got to closest worker')
            self.missions['missions'] = name

    def action_cart_harvest(self) -> None:
        """Cart action move to closest resource
        """
        logger.info('> action_cart_harvest: im here and go to closest worker')
        self._move_to_closest_action(
            tiles=self.tiles_collection.player_workers
            )


class PerformMissionsAndActions:
    """This class construct all possible missions and actions for all objects
    that can act
    """
   
    def __init__(
        self, 
        tiles_collection: TilesCollection, 
        states_collections: StatesCollectionsCollection,
        missions_state: MissionState,
        obj_: GameActiveObjects
        ) -> None:
        self.tiles_collection = tiles_collection
        self.states_collections = states_collections
        self.missions_state = missions_state
        self.obj  = obj_ 

    def _iterate_missions(
        self, 
        cls_: Union[WorkerMission, CartMission, CityMission],
        mission: str = None
        ) -> Tuple[Missions, MissionState, CheckAgain]:
        """Iterate missions for get all actions for object

        Args:
            cls (Union[WorkerMission, CartMission, CityMission]): mission class
            of object
            mission (str): mission of object, default None

        Returns:
            Tuple[Dict[str, Union[Unit, CityTile, List[str]]], Dict[str, str], Unit]:
            missions. mission_state and check_again
        """
        perform = cls_(
            tiles_collection=self.tiles_collection,
            states_collections=self.states_collections,
            missions_state=self.missions_state,
            obj_=self.obj
            )
        if mission:
            logger.info(f'> _iterate_missionss mission: {mission}')
            class_method = getattr(cls_, mission)
            logger.info(f'> _iterate_missionss class_method: {class_method}')
            class_method(perform)
        else:
            per = [method for method in dir(cls_) if method.startswith('mission_')]
            for met in per:
                class_method = getattr(cls_, met)
                class_method(perform)
        return perform.missions, perform.missions_state, perform.check_again

    def perform_missions(self) -> Tuple[
        Dict[str, Union[Unit, CityTile, List[str]]], 
        Dict[str, str],
        Unit
        ]:
        """Check all, set or cancel missions and mission_statement

        Returns:
            Tuple[Dict[str, Union[Unit, CityTile, List[str]]], Dict[str, str], Unit]:
            missions. mission_state and check_again
        """
        if self.obj.can_act():
            if isinstance(self.obj, Unit):
                logger.info('> perform_missions_and_actions: im unit')
                if self.obj.is_worker():
                    logger.info('> perform_missions_and_actions: im worker')
                    cls_ = WorkerMission
                if self.obj.is_cart():
                    logger.info('> perform_missions_and_actions: im cart')
                    cls_ = CartMission
                if self.obj.id in self.missions_state.keys():
                    logger.info('> perform_missions_and_actions: i have mission from previous turn - ' +
                        f'{self.missions_state[self.obj.id]}')
                    return self._iterate_missions(cls_=cls_, mission=self.missions_state[self.obj.id])
            if isinstance(self.obj, CityTile):
                logger.info('> perform_missions_and_actions: im citytile')
                cls_ = CityMission
            logger.info('> perform_missions_and_actions: no mission from previous turn')
            return self._iterate_missions(cls_=cls_, mission=None)
        
    def perform_missions_actions(self) -> Tuple[
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
                logger.info('> perform_missions_and_actions: im unit')
                if self.obj.is_worker():
                    logger.info('> perform_missions_and_actions: im worker')
                    cls_ = WorkerMission
                if self.obj.is_cart():
                    logger.info('> perform_missions_and_actions: im cart')
                    cls_ = CartMission
                if self.obj.id in self.missions_state.keys():
                    logger.info('> perform_missions_and_actions: i have mission from previous turn - ' +
                        f'{self.missions_state[self.obj.id]}')
                    return self._iterate_missions(cls_=cls_, mission=self.missions_state[self.obj.id])
            if isinstance(self.obj, CityTile):
                logger.info('> perform_missions_and_actions: im citytile')
                cls_ = CityMission
            logger.info('> perform_missions_and_actions: no mission from previous turn')
            return self._iterate_missions(cls_=cls_, mission=None)

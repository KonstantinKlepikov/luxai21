from lux.game_objects import Unit, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs, get_id
from bots.statements import (
    TileState, TilesCollection, TileStatesCollection
)
from bots.utility import (
    GameActiveObjects, GameCellObjects, MissionsState, 
    Missions, CheckAgain, AvailablePos
)
from typing import List, Tuple, Union
import os, sys, math, random


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
    
    NOTE: We add mission as key to self.action dict. As value we add
    action string or None if no any action needed in this mission on this turn
    
    NOTE: We add new object id and his mission string to self.missions_state or remove
    ended mission
    
    NOTE: self.check_again is used for check unit for new mission, when old is removed
    """
   
    def __init__(
        self, 
        tiles: TilesCollection, 
        states: TileStatesCollection,
        missions_state: MissionsState,
        obj_: GameActiveObjects
        ) -> None:
        self.tiles = tiles
        self.states = states
        self.missions_state = missions_state
        self.obj = obj_
        self.missions:  Missions = {'obj': obj_, 'missions': []}
        self.action: str = None
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
    """Citytile object missions with his possible actions
    
    NOTE: Citytile can't add his missions to mission_state, because
    its missions is continue no longer than one turn
    """
    current_turn = -1
    build_units_counter = 0

    def __init__(
        self,
        tiles: TilesCollection,
        states: TileStatesCollection,
        missions_state: MissionsState,
        obj_: GameActiveObjects
        ) -> None:
        super().__init__(tiles, states, missions_state, obj_)
        self.__can_build = None
        self.build_unit = False
        if CityMission.current_turn != states.turn:
            CityMission.current_turn = states.turn
            CityMission.build_units_counter = 0
            logger.warning(f'=====Turn {self.current_turn} =====')

    @property
    def _can_build(self) -> bool:  # TODO: move to StatesCollection
        """Set citytile can build
        
        City cant build units if citytiles == units, owned by player
        """
        if self.__can_build is None:
            city_units_diff = len(self.tiles.player_citytiles) - len(self.tiles.player_units)
            logger.warning(f'Cities: {", ".join(get_id(city) for city in self.tiles.player_cities)}; '
                           f'Citytiles: {", ".join(str(tile.pos) for tile in self.tiles.player_citytiles)}; '
                           f'Units: {len(self.tiles.player_units)}')
            if city_units_diff > 0:
                self.__can_build = (city_units_diff - CityMission.build_units_counter) > 0
                logger.warning(f'Tile {get_id(self.obj)}; {self.__can_build=}; '
                               f'counter={CityMission.build_units_counter}')
        return self.__can_build

    def mission_research(self) -> None:
        """Citytile research mission
        """
        name = self.mission_research.__name__
        if not self.tiles.player.researched_uranium():
            logger.info('> citytile mission_research added')
            self.missions['missions'].append(name)
            
    def action_research(self, available_pos: AvailablePos) -> None:
        """Citytile research action
        """
        logger.info('> citytile action_research added')
        self.action = self.obj.research()  

    def mission_build_worker(self) -> None:
        """Citytile build worker mission
        """
        name = self.mission_build_worker.__name__
        if self._can_build:
            logger.info('> citytile mission_build_worker added')
            self.missions['missions'].append(name)
            if not self.build_unit:
                CityMission.build_units_counter += 1
                self.build_unit = True
            logger.warning(f'BW Counter={CityMission.build_units_counter}')

    def action_build_worker(self, available_pos: AvailablePos) -> None:
        """Citytile build worker action
        """
        logger.info('> citytile action_build_worker added')
        self.action = self.obj.build_worker()

    def mission_build_cart(self) -> None:
        """Citytile build cart mission
        """
        name = self.mission_build_cart.__name__
        if self._can_build:
            logger.info('> citytile mission_build_cart added')
            self.missions['missions'].append(name)
            if not self.build_unit:
                CityMission.build_units_counter += 1
                self.build_unit = True
            logger.warning(f'BC Counter={CityMission.build_units_counter}')

    def action_build_cart(self, available_pos: AvailablePos) -> None:
        """Citytile build cart action
        """
        logger.info('> citytile action_build_cart added')
        self.action = self.obj.build_cart()


class UnitMission(Mission):
    """Missions for units of any type
    """

    def __init__(
        self,
        tiles: TilesCollection,
        states: TileStatesCollection,
        missions_state: MissionsState,
        obj_: GameActiveObjects
        ) -> None:
        super().__init__(tiles, states, missions_state, obj_)
        self.__adjacent_tile_states = None

    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: current tile statement object
        """
        return self.states.get_state(pos=self.obj.pos)
    
    @property 
    def _adjacent_tile_states(self) -> List[TileState]: # TODO: move to independed class
        """Get list of statements of adjacent tiles

        Returns:
            list of statements of adjacent tiles
        """
        if self.__adjacent_tile_states is None:
            adjacent = self._current_tile_state.adjacent
            states = []
            for pos in adjacent:
                tile_state = self.states.get_state(pos=pos)
                states.append(tile_state)
            self.__adjacent_tile_states = states
        return self.__adjacent_tile_states
    
    def _collision_resolution(self, target: Position, available_pos: AvailablePos) -> None:
        """Define move action of unit with collision resolution

        Args:
            target (Position): position of target cell
            available_pos (AvailablePos): dict wih directions and tuple with
            positions x, y
        """
        adj_dir = self._current_tile_state.adjacent_dir_tuples
        # dir_to_target = self.obj.pos.direction_to(target)
        logger.info(f'> _collision_resolution: available_pos {available_pos}')
        logger.info(f'> _collision_resolution: adjacent_dir {adj_dir}')
        logger.info(f'> _collision_resolution: dir_to_target {self.obj.pos.direction_to(target)}')
        logger.info(f'> _collision_resolution: obj position {self.obj.pos.x}, {self.obj.pos.y}')
        logger.info(f'> _collision_resolution: target position {target.x}, {target.y}')

        way = None

        if self.obj.pos.x == target.x:
            if self.obj.pos.y > target.y:
                way = ['n', 'e', 'w', 's']
            if self.obj.pos.y < target.y:
                way = ['s', 'e', 'w', 'n']
        elif self.obj.pos.x > target.x:
            if self.obj.pos.y >= target.y:
                way = ['w', 's', 'e', 'n']
            else:
                way = ['w', 'n', 'e', 's']
        elif self.obj.pos.x < target.x:
            if self.obj.pos.y >= target.y:
                way = ['e', 's', 'w', 'n']
            else:
                way = ['e', 'n', 's', 'w']
        logger.info(f'> _collision_resolution: way: {way}')

        if way:
            for dir in way:
                try:
                    if adj_dir[dir] in available_pos:
                        self.action = self.obj.move(dir)
                        available_pos.discard(adj_dir[dir])
                        logger.info(f'> _collision_resolution: action {self.action}')
                        logger.info(f'> _collision_resolution: available_pos {available_pos}')
                        break
                except KeyError:
                    logger.info(f'> _collision_resolution: broken position {dir}')
                    continue

    def _move_to_closest_action(
        self,
        tiles: List[Cell],
        available_pos: AvailablePos
        ) -> None:
        """Get move to closest tile of given type action

        Args:
            name (str): name of mission method
            tiles (List[Cell]): list of tiles for closest calculation
            available_pos (AvailablePos): dict wih directions and tuple with
            positions x, y

        TODO: we need list of targets for moving, not closest for all
        """
        closest = self._get_closest_pos(tiles)
        if closest:            
            self._collision_resolution(target=closest, available_pos=available_pos)

    def _transfer_resource(self) -> None:
        """Transfere resource to cart action
        
        NOTE: transfer(dest_id, resourceType, amount): str - returns the transfer action. Will 
        transfer from this Unit the selected Resource type by the desired amount to the Unit 
        with id dest_id given that both units are adjacent at the start of the turn. (This means 
        that a destination Unit can receive a transfer of resources by another Unit but also 
        move away from that Unit)
        
        NOTE: Transfer - Send any amount of a single resource-type from a unit's cargo to another 
        (start-of-turn) adjacent Unit, up to the latter's cargo capacity. Excess is returned to 
        the original unit.
        """
        # init all unit objects in collection of tile states
        self.states.player_active_obj_to_state

        adjacence = self._adjacent_tile_states
        logger.info(f'> _transfer_resource: adjacence {adjacence}')

        for state in adjacence:
            logger.info(f'> _transfer_resource: state {state}')
            if state.player_cart_object and state.player_cart_object.get_cargo_space_left():
                logger.info('> _transfer_resource: cart is adjacent and has empty space')
                logger.info(f'> _transfer_resource: cart id {state.player_cart_object.id}')
                logger.info(f'> _transfer_resource: cart cargo left {state.player_cart_object.get_cargo_space_left()}')
                logger.info(f'> _transfer_resource: action {self.action}')
                if self.obj.cargo.uranium:
                    logger.info(f'> _transfer_resource: transfer uranium {self.obj.cargo.uranium}')
                    self.action = self.obj.transfer(
                        dest_id=state.player_cart_object.id,
                        resourceType=cs.RESOURCE_TYPES.URANIUM,
                        amount=self.obj.cargo.uranium
                        )
                elif self.obj.cargo.coal:
                    logger.info(f'> _transfer_resource: transfer coal {self.obj.cargo.coal}')
                    self.action = self.obj.transfer(
                        dest_id=state.player_cart_object.id,
                        resourceType=cs.RESOURCE_TYPES.COAL,
                        amount=self.obj.cargo.coal
                        )
                elif self.obj.cargo.wood:
                    logger.info(f'> _transfer_resource: transfer wood {self.obj.cargo.wood}')
                    self.action = self.obj.transfer(
                        dest_id=state.player_cart_object.id,
                        resourceType=cs.RESOURCE_TYPES.WOOD,
                        amount=self.obj.cargo.wood
                        )
                else:
                    logger.info('> _transfer_resource: nothing to transfer')
            else:
                logger.info('> _transfer_resource: no adjacent carts or is fool')
            logger.info(f'> _transfer_resource: action {self.action}')

    def _end_mission(self) -> None:
        """End mission and add object to check_again
        """
        if self.obj.id in self.missions_state.keys():
            self.missions_state.pop(self.obj.id, None)
            self.check_again = self.obj
            logger.info(f'> _end_mission: i try end mission. missions_state: {self.missions_state}')
            logger.info(f'> _end_mission: i end mission. missions_state: {self.missions_state}')

    def mission_drop_the_resources(self) -> None:
        """Move to closest city mission
        
        NOTE: we dont check how many capacity unit has. We check - is completely empty?
        If it is empty - it cant move to drop his resources.
        """
        name = self.mission_drop_the_resources.__name__
        if not self.obj.get_cargo_space_left():
            logger.info('> mission_drop_the_resources: im fool')
            if self._current_tile_state.is_city:
                logger.info('> mission_drop_the_resources: im in city and drop this mission')
                self._end_mission()
            else:
                logger.info('> mission_drop_the_resources: im not in city')
                if self.tiles.player_citytiles:
                    logger.info('> mission_drop_the_resources: citityles is exist')
                    self.missions['missions'].append(name)
        else:
            logger.info('> mission_drop_the_resources: im empty and drop this mission')
            self._end_mission()
    
    def action_drop_the_resources(self, available_pos: AvailablePos) -> None:
        """Move to closest city action
        
        NOTE: if it possible - drop resources to cart
        """
        if self.obj.is_worker:
            logger.info('> action_drop_the_resources: im worker and try drop resources')
            self._transfer_resource()
        if not self.action:
            logger.info('> action_drop_the_resources: im go to closest city')
            self._move_to_closest_action(
                tiles=self.tiles.player_citytiles,
                available_pos=available_pos
                )


class WorkerMission(UnitMission):
    """Worker missions with his posible actions
    """

    def mission_mine_resource(self) -> None:
        """Worker mission for mining resources
        
        NOTE: we dont check how many capacity unit has. We check - is it fool?
        If it is fool - it cant mine.
        """
        name = self.mission_mine_resource.__name__
        if not self.obj.get_cargo_space_left():
            logger.info('> mission_mine_resource: im fool')
            self._end_mission()
        else:
            logger.info('> mission_mine_resource: im empty')
            self.missions['missions'].append(name)
    
    def action_mine_resource(self, available_pos: AvailablePos) -> None:
        """Worker action for mining resources
        """
        logger.info('> action_mine_resource: im here')
        logger.info(f'> action_mine_resource: available_pos: {available_pos}')
        if self._current_tile_state.is_city:
            logger.info('> action_mine_resource: im in city and go mine')
            self._move_to_closest_action(
                tiles=self.tiles.resources,
                available_pos=available_pos
                )
        else:
            adjacence = self._adjacent_tile_states
            main_now = False
            for state in adjacence: 
                if state.is_wood:
                    logger.info('> action_mine_resource: i mine wood')
                    main_now = True
                    break
                elif self.tiles.player.researched_coal() and state.is_coal:
                    logger.info('> action_mine_resource: i mine coal')
                    main_now = True
                    break
                elif self.tiles.player.researched_uranium() and state.is_uranium:
                    logger.info('action_mine_resource: i mine uranium')
                    main_now = True
                    break
            if not main_now:
                logger.info('> action_mine_resource: im not in city and go mine')
                if self.tiles.player.researched_uranium():
                    logger.info('> action_mine_resource: im go mine uranium')
                    self._move_to_closest_action(
                        tiles=self.tiles.uraniums,
                        available_pos=available_pos
                        )
                elif self.tiles.player.researched_coal():
                    logger.info('> action_mine_resource: im go mine coal')
                    self._move_to_closest_action(
                        tiles=self.tiles.coals,
                        available_pos=available_pos
                        )
                else:
                    logger.info('> action_mine_resource: im go mine wood')
                    self._move_to_closest_action(
                        tiles=self.tiles.woods,
                        available_pos=available_pos
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
            self.missions['missions'].append(name)
                
    def action_buld_the_city(self, available_pos: AvailablePos) -> None:
        """Worker action to build a city
        """
        logger.info('> action_buld_the_city: im here')
        if self.obj.can_build(self.tiles.game_state.map):
            logger.info('> action_buld_the_city: i build the city')
            self.action = self.obj.build_city()
        else:
            logger.info('> action_buld_the_city: i move random')
            seq = list(cs.DIRECTIONS)
            self.action = self.obj.move(random.choice(seq=seq))


class CartMission(UnitMission):
    """Cart missions with his posible actions
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
            self.missions['missions'].append(name)

    def action_cart_harvest(self, available_pos: AvailablePos) -> None:
        """Cart action move to closest resource
        """
        logger.info('> action_cart_harvest: im here and go to closest worker')
        self._move_to_closest_action(
            tiles=self.tiles.player_workers,
            available_pos=available_pos
            )


class Perform:
    """Base class construct all possible missions and actions for all objects
    that can act
    """
    
    def __init__(
        self, 
        tiles: TilesCollection, 
        states: TileStatesCollection,
        missions_state: MissionsState,
        obj_: GameActiveObjects
        ) -> None:
        self.tiles = tiles
        self.states = states
        self.missions_state = missions_state
        self.obj  = obj_


class PerformMissions(Perform):
    """This class construct all possible missions for all objects
    that can act
    """

    def _iterate_missions(
        self, 
        cls_: Union[WorkerMission, CartMission, CityMission],
        mission: str = None
        ) -> Tuple[Missions, MissionsState, CheckAgain]:
        """Iterate missions for get all missions for all objects

        Args:
            cls (Union[WorkerMission, CartMission, CityMission]): mission class
            of object
            mission (str, optional): mission. Defaults to None

        Returns:
            missions, mission_state and check_again
        """
        perform = cls_(
            tiles=self.tiles,
            states=self.states,
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
        Missions,
        MissionsState,
        CheckAgain
        ]:
        """Set or cancel missions and set mission_statement

        Returns:
            missions. mission_state and check_again
        """
        if self.obj.can_act():
            if isinstance(self.obj, Unit):
                logger.info('> perform_missions: im unit')
                if self.obj.is_worker():
                    logger.info('> perform_missions: im worker')
                    cls_ = WorkerMission
                if self.obj.is_cart():
                    logger.info('> perform_missions: im cart')
                    cls_ = CartMission
                if self.obj.id in self.missions_state.keys():
                    logger.info('> perform_missions: i have mission from previous turn - ' +
                        f'{self.missions_state[self.obj.id]}')
                    return self._iterate_missions(cls_=cls_, mission=self.missions_state[self.obj.id])
            if isinstance(self.obj, CityTile):
                logger.info('> perform_missions: im citytile')
                cls_ = CityMission
            logger.info('> perform_missions: no mission from previous turn')
            return self._iterate_missions(cls_=cls_, mission=None)
        
class PerformActions(Perform):
    """This class construct all possible actions for all objects
    that can act
    
        available_pos: AvailablePos: dict wih directions and tuple with
        positions x, y
    """
   
    def __init__(
        self, 
        tiles: TilesCollection, 
        states: TileStatesCollection,
        missions_state: MissionsState,
        obj_: GameActiveObjects,
        available_pos: AvailablePos
        ) -> None:
        super().__init__(tiles, states, missions_state, obj_)
        self.available_pos = available_pos

    def _get_action(
        self, 
        cls_: Union[WorkerMission, CartMission, CityMission],
        mission: str = None
        ) -> str:
        """[summary]

        Args:
            cls_ (Union[WorkerMission, CartMission, CityMission]): mission class
            mission (str, optional): mission. Defaults to None.

        Returns:
            str: action
        """
        perform = cls_(
            tiles=self.tiles,
            states=self.states,
            missions_state=self.missions_state,
            obj_=self.obj
            )
        logger.info(f'> _get_action mission: {mission}')
        act = mission.replace("mission_", "action_")
        logger.info(f'> _get_action action: {act}')
        class_method = getattr(cls_, act)
        logger.info(f'> _get_action class_method: {class_method}')
        class_method(perform, self.available_pos)
        return perform.action

    def perform_actions(self, miss: str) -> str:
        """Set action

        Returns:
            str: choosed action
        """
        if isinstance(self.obj, Unit):
            logger.info('> perform_actions: im unit')
            if self.obj.is_worker():
                logger.info('> perform_actions: im worker')
                cls_ = WorkerMission
            if self.obj.is_cart():
                logger.info('> perform_actions: im cart')
                cls_ = CartMission
        if isinstance(self.obj, CityTile):
            logger.info('> perform_actions: im citytile')
            cls_ = CityMission
        return self._get_action(cls_=cls_, mission=miss)


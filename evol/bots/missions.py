from lux.game_objects import Unit, CityTile
from lux.game_map import Position
from bots.utility import CONSTANTS as cs
from bots.statements import (
    TurnSpace, TileState
)
from bots.utility import (
    GameActiveObject, MissionsState, 
    Missions, UnicPos, Coord, AD
)
from typing import List, Tuple, Union, Set
import os, sys, random

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
    
    NOTE: We add new object id and his mission string to missions_state or remove
    ended mission
    
    NOTE: self.check_again is used for check unit for new mission, when old is removed
    """
   
    def __init__(
        self, 
        turn_space: TurnSpace,
        obj_: GameActiveObject
        ) -> None:
        self.turn_space = turn_space
        self.obj = obj_
        self.missions:  Missions = {'obj': obj_, 'missions': []}
        self.action: str = None
        self.check_again: GameActiveObject = None

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

    def _get_closest_pos(self, positions: List[Position]) -> Position:
        """Get closest position

        Args:
            positions (list): list of objects

        Returns:
            Position: closest Position object
        """
        distance = AD[self.turn_space.tiles.game_state.map_height]['distance'][(self.obj.pos.x, self.obj.pos.y)]
        dist = {
            val: key
            for key, val in distance.items()
            if Position(key[0], key[1]) in positions
            }
        if dist:
            min_value = min(dist.keys())
            pos = dist[min_value]
            closest_pos = Position(pos[0], pos[1])
            return closest_pos

class CityMission(Mission):
    """Citytile object missions with his possible actions
    
    NOTE: Citytile can't add his missions to missions_state, because
    its missions is continue no longer than one turn
    """

    def __init__(
        self,
        turn_space: TurnSpace,
        obj_: GameActiveObject
        ) -> None:
        super().__init__(turn_space, obj_)

    def mission_research(self) -> None:
        """Citytile research mission
        """
        name = self.mission_research.__name__
        if not self.turn_space.tiles.player.researched_uranium():
            logger.info('> citytile mission_research added')
            self.missions['missions'].append(name)

    def action_research(self) -> None:
        """Citytile research action
        """
        logger.info('> citytile action_research added')
        self.action = self.obj.research()  

    def mission_build_worker(self) -> None:
        """Citytile build worker mission
        """
        logger.info('> mission_build_worker: im here')
        name = self.mission_build_worker.__name__
        if self.turn_space.tiles.city_units_diff > 0:
            self.missions['missions'].append(name)
            logger.info('> mission_build_worker added')

    def action_build_worker(self) -> None:
        """Citytile build worker action
        """
        logger.info('> action_build_worker added')
        self.action = self.obj.build_worker()

    def mission_build_cart(self) -> None:
        """Citytile build cart mission
        """
        logger.info('> mission_build_cart: im here')
        name = self.mission_build_cart.__name__
        if self.turn_space.tiles.city_units_diff > 0:
            self.missions['missions'].append(name)
            logger.info('> mission_build_cart: added')

    def action_build_cart(self) -> None:
        """Citytile build cart action
        """
        logger.info('> citytile action_build_cart added')
        self.action = self.obj.build_cart()


class UnitMission(Mission):
    """Missions for units of any type
    """
    
    available_pos: UnicPos = None
    adj_coord_unic: Set[Coord] = None

    def __init__(
        self,
        turn_space: TurnSpace,
        obj_: GameActiveObject
        ) -> None:
        super().__init__(turn_space, obj_)
        self.__adjacent_tile_states = None

    @property
    def _current_tile_state(self) -> TileState:
        """Current cell statement

        Returns:
            TileState: current tile statement object
        """
        return self.turn_space.states.get_state(pos=self.obj.pos)
    
    @property 
    def _adjacent_tile_states(self) -> List[TileState]: # TODO: move to independed class
        """Get list of statements of adjacent tiles

        Returns:
            list of statements of adjacent tiles
        """
        if self.__adjacent_tile_states is None:
            adjacent = self._current_tile_state.adjacent_pos
            states = []
            for pos in adjacent:
                tile_state = self.turn_space.states.get_state(pos=pos)
                states.append(tile_state)
            self.__adjacent_tile_states = states
        return self.__adjacent_tile_states
    
    def _collision_resolution(self, target: Position) -> None:
        """Define move action of unit with collision resolution

        Args:
            target (Position): position of target cell
            available_pos (UnicPos): dict wih directions and tuple with
            positions x, y
        """
        adj_dir = self._current_tile_state.adjacent_dir_unic_pos
        logger.info(f'> _collision_resolution: available_pos {self.available_pos}')
        logger.info(f'> _collision_resolution: adjacent_dir {adj_dir}')
        logger.info(f'> _collision_resolution: dir_to_target {self.obj.pos.direction_to(target)}')
        logger.info(f'> _collision_resolution: obj position {self.obj.pos.x}, {self.obj.pos.y}')
        logger.info(f'> _collision_resolution: target position {target.x}, {target.y}')

        way = None

        if self.obj.pos.x == target.x: # TODO: refactoring - ambiqulous
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
                    if adj_dir[dir] in self.available_pos:
                        self.action = self.obj.move(dir)
                        self.available_pos.discard(adj_dir[dir])
                        logger.info(f'> _collision_resolution: action {self.action}')
                        logger.info(f'> _collision_resolution: available_pos {self.available_pos}')
                        break
                except KeyError:
                    logger.info(f'> _collision_resolution: broken position {dir}')
                    continue

    def _move_to_closest(self, pos: List[Position]) -> None:
        """Get move to closest tile of given type action

        Args:
            pos (List[Position]): list of positions for closest calculation
        """
        closest = self._get_closest_pos(pos)
        if closest:            
            self._collision_resolution(target=closest)
            
    def _move_to_closest_available_tile_to_mine(self) -> None:
        """Get move to closest available tile to main
        """
        self.turn_space.adjcollection.adj_coord_unic = self.adj_coord_unic
        logger.info(
            '> _move_to_closest_available_tile_to_mine: len adj_coord_unic '
            f'{len(self.adj_coord_unic)}'
            )
        if self.turn_space.tiles.player.researched_uranium():
            logger.info('> _move_to_closest_available_tile_to_mine: im go mine uranium')
            positions = self.turn_space.adjcollection.empty_adjacent_any_pos
        elif self.turn_space.tiles.player.researched_coal():
            logger.info('> _move_to_closest_available_tile_to_mine: im go mine coal')
            positions = self.turn_space.adjcollection.empty_adjacent_wood_coal_pos
        else:
            logger.info('> _move_to_closest_available_tile_to_mine: im go mine wood')
            positions = self.turn_space.adjcollection.empty_adjacent_wood_pos

        logger.info(f'> _move_to_closest_available_tile_to_mine: positions {len(positions)}')
        closest = self._get_closest_pos(positions=positions)
        logger.info(f'> _move_to_closest_available_tile_to_mine: closest {closest}')
        if closest:
            self._collision_resolution(target=closest)
            logger.info(f'> _move_to_closest_available_tile_to_mine: action {self.action}')
            if self.action:
                cell = self.turn_space.tiles.game_state.map.get_cell_by_pos(closest)
                logger.info(f'> _move_to_closest_available_tile_to_mine: cell {cell}')
                self.adj_coord_unic.discard((closest.x, closest.y))
                logger.info(
                    '> _move_to_closest_available_tile_to_mine: len adj_coord_unic after remove '
                    f'{len(self.adj_coord_unic)}'
                    )

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
        if self.obj.id in self.turn_space.game_space.missions_state.keys():
            self.turn_space.game_space.missions_state.pop(self.obj.id, None)
            self.check_again = self.obj
            logger.info(f'> _end_mission: i try end mission. missions_state: {self.turn_space.game_space.missions_state}')
            logger.info(f'> _end_mission: i end mission. missions_state: {self.turn_space.game_space.missions_state}')

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
                if self.turn_space.tiles.player_citytiles:
                    logger.info('> mission_drop_the_resources: citityles is exist')
                    self.missions['missions'].append(name)
        else:
            logger.info('> mission_drop_the_resources: im empty and drop this mission')
            self._end_mission()
    
    def action_drop_the_resources(self) -> None:
        """Move to closest city action
        
        NOTE: if it possible - drop resources to cart
        """
        if self.obj.is_worker:
            logger.info('> action_drop_the_resources: im worker and try drop resources')
            self._transfer_resource()
        if not self.action:
            logger.info('> action_drop_the_resources: im go to closest city')
            self._move_to_closest(pos=self.turn_space.tiles.player_citytiles_pos)


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

    def action_mine_resource(self) -> None: # FIXME: rewrite if hamburger
        """Worker action for mining resources
        """
        logger.info('> action_mine_resource: im here')
        logger.info(f'> action_mine_resource: available_pos: {self.available_pos}')
        if self._current_tile_state.is_city:
            logger.info('> action_mine_resource: im in city')
            main_now = False
        else:
            main_now = False
            adjacence = self._adjacent_tile_states
            for state in adjacence: 
                if state.is_wood:
                    logger.info('> action_mine_resource: i mine wood')
                    main_now = True
                    break
                elif self.turn_space.tiles.player.researched_coal() and state.is_coal:
                    logger.info('> action_mine_resource: i mine coal')
                    main_now = True
                    break
                elif self.turn_space.tiles.player.researched_uranium() and state.is_uranium:
                    logger.info('action_mine_resource: i mine uranium')
                    main_now = True
                    break
        if not main_now:
            self._move_to_closest_available_tile_to_mine()
        

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
                
    def action_buld_the_city(self) -> None:
        """Worker action to build a city
        """
        logger.info('> action_buld_the_city: im here')
        if self.obj.can_build(self.turn_space.tiles.game_state.map):
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

    def action_cart_harvest(self) -> None:
        """Cart action move to closest resource
        """
        logger.info('> action_cart_harvest: im here and go to closest worker')
        self._move_to_closest(pos=self.turn_space.tiles.player_workers_pos)


class Perform:
    """Base class construct all possible missions and actions for all objects
    that can act
    """
    
    def __init__(
        self,
        turn_space: TurnSpace,
        obj_: GameActiveObject
        ) -> None:
        self.turn_space = turn_space
        self.obj  = obj_


class PerformMissions(Perform):
    """This class construct all possible missions for all objects
    that can act
    """

    def _iterate_missions(
        self, 
        cls_: Union[WorkerMission, CartMission, CityMission],
        mission: str = None
        ) -> Tuple[Missions, GameActiveObject]:
        """Iterate missions for get all missions for all objects

        Args:
            cls (Union[WorkerMission, CartMission, CityMission]): mission class
            of object
            mission (str, optional): mission. Defaults to None

        Returns:
            missions and check_again
        """
        perform = cls_(
            turn_space=self.turn_space,
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
        return perform.missions, perform.check_again

    def perform_missions(self) -> Tuple[
        Missions,
        MissionsState,
        GameActiveObject
        ]:
        """Set or cancel missions and set missions_statement

        Returns:
            missions and check_again
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
                if self.obj.id in self.turn_space.game_space.missions_state.keys():
                    logger.info('> perform_missions: i have mission from previous turn - ' +
                        f'{self.turn_space.game_space.missions_state[self.obj.id]}')
                    return self._iterate_missions(
                        cls_=cls_,
                        mission=self.turn_space.game_space.missions_state[self.obj.id]
                        )
            if isinstance(self.obj, CityTile):
                logger.info('> perform_missions: im citytile')
                cls_ = CityMission
            logger.info('> perform_missions: no mission from previous turn')
            return self._iterate_missions(cls_=cls_, mission=None)
        
class PerformActions(Perform):
    """This class construct all possible actions for all objects
    that can act
    
        available_pos: UnicPos: dict wih directions and tuple with
        positions x, y
    """
   
    def __init__(
        self,
        turn_space: TurnSpace,
        obj_: GameActiveObject,
        available_pos: UnicPos,
        ) -> None:
        super().__init__(turn_space, obj_)
        self.available_pos = available_pos
        self.adj_coord_unic = turn_space.game_space.adj_coord_unic.copy()

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
            turn_space=self.turn_space,
            obj_=self.obj
            )
        logger.info(f'> _get_action mission: {mission}')
        act = mission.replace("mission_", "action_")
        logger.info(f'> _get_action action: {act}')
        class_method = getattr(cls_, act)
        logger.info(f'> _get_action class_method: {class_method}')
        class_method(perform)
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
                cls_.adj_coord_unic = self.adj_coord_unic
            if self.obj.is_cart():
                logger.info('> perform_actions: im cart')
                cls_ = CartMission
            cls_.available_pos = self.available_pos
            
        if isinstance(self.obj, CityTile):
            logger.info('> perform_actions: im citytile')
            cls_ = CityMission
        return self._get_action(cls_=cls_, mission=miss)

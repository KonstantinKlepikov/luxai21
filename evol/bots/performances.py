from lux.game_objects import Unit, CityTile
from bots.utility import CONSTANTS as cs
from bots.statements import TileState, TilesCollection, StatesCollectionsCollection
from typing import List, Dict, Union
import os, sys


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


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
 
 
class UnitPerformance(Performance):
    
    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)
        self.actions = {'obj': obj_}
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
            self.actions[self.perform_move_to_city.__name__] = None

    def perform_transfer(self) -> None:
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
            self.actions[self.perform_move_to_resource.__name__] = None

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
            self.actions[self.perform_build_city.__name__] = None


class CartPerformance(UnitPerformance):
    """Perform cart object with his posible actions
    """

    def perform_move_to_worker(self) -> None:
        """Perform move to closest resource
        """
        if self.obj.get_cargo_space_left():
            self.actions[self.perform_move_to_worker.__name__] = None


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
            self.actions[self.perform_research.__name__] = None

    def perform_build_worker(self) -> None:
        """Perform citytile build worker
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions[self.perform_build_worker.__name__] = None

    def perform_build_cart(self) -> None:
        """Perform citytile build cart
        
        City cant build units if citytiles == units, owned by player
        """
        if self._can_build:
            self.actions[self.perform_build_cart.__name__] = None


class PerformAndGetActions(Performance):
    
    def __init__(
        self,
        tiles_collection: TilesCollection,
        states_collection: StatesCollectionsCollection,
        obj_: Union[Unit, CityTile]
        ) -> None:
        super().__init__(tiles_collection, states_collection, obj_)
        
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

# class UnitPerformance:
#     """Perform unit object with his possible actions
#     """
#     def __init__(
#         self, 
#         tiles_collection: TilesCollection, 
#         states_collection: StatesCollectionsCollection, 
#         unit: Unit
#         ) -> None:
#         self.unit = unit
#         self.tiles_collection = tiles_collection
#         self.states_collection = states_collection
#         self.__current_tile_state = None
#         self.__ajacent_tile_states = None
#         self.actions = {'obj': unit}
#         self.geometric = Geometric(unit.pos)

#     @property
#     def _current_tile_state(self) -> TileState:
#         """Current cell statement

#         Returns:
#             TileState: statements
#         """
#         if self.__current_tile_state is None:
#             self.__current_tile_state = self.states_collection.get_state(pos=self.unit.pos)

#         return self.__current_tile_state

#     @property 
#     def _ajacent_tile_states(self) -> List[TileState]:
#         """Get list of statements of ajacent tiles

#         Returns:
#             list: list of statements
#         """
#         if self.__ajacent_tile_states is None:
#             ajacent = self.geometric.get_ajacent_positions() # TODO: use from TileState
#             states = []
#             for pos in ajacent:
#                 try: # FIXME: list index out of range (it is temporal solution)
#                     tile_state = self.states_collection.get_state(pos=pos)
#                     states.append(tile_state)
#                 except IndexError:
#                     continue
#             self.__ajacent_tile_states = states
 
#         return self.__ajacent_tile_states

#     def _set_move(self) -> None:
#         """Set move action
#         """
#         if self.unit.get_cargo_space_left():
#             self.actions['move_to_closest_resource'] = None
#         else:
#             self.actions['move_to_closest_citytile'] = None
#         self.actions['move_random'] = None

#     def _set_transfer(self) -> None:
#         """Set transfer action
#         """
#         for state in self._ajacent_tile_states: # TODO: move to tolestatements
#             if state.is_owned_by_player:
#                 if state.is_worker and (cs.RESOURCE_CAPACITY.WORKER - self.unit.get_cargo_space_left()):
#                     self.actions['transfer'] = None
#                     break
#                 elif state.is_cart and (cs.RESOURCE_CAPACITY.CART - self.unit.get_cargo_space_left()):
#                     self.actions['transfer'] = None
#                     break

#     def _set_mine(self) -> None:
#         """Set mine action
        
#         Units cant mine from the cityes
#         """
#         if self.unit.get_cargo_space_left() and not self._current_tile_state.is_city:
#             for state in self._ajacent_tile_states:
#                 if state.is_wood:
#                     self.actions['mine'] = None
#                     break
#                 elif self.tiles_collection.player.researched_coal() and state.is_coal:
#                     self.actions['mine'] = None
#                     break
#                 elif self.tiles_collection.player.researched_uranium() and state.is_uranium:
#                     self.actions['mine'] = None
#                     break

#     def _set_pillage(self) -> None:
#         """Set pillage action
        
#         Roads can be created only by carts. Roads dont have owners. 
#         Citytiles has 6 road status by defoult
#         """
#         if self._current_tile_state.is_road:
#             self.actions['pillage'] = None

#     def _set_build_city(self) -> None:
#         """Set build city action
#         """
#         if self.unit.can_build(self.tiles_collection.game_state.map):
#             self.actions['build'] = None

#     def get_actions(self) -> dict:
#         """Set all possible actions

#         Returns:
#             dict: object and his posible actions
#         """
#         self.actions['u_pass'] = None
#         if self.unit.can_act():
#             self._set_move()
#             self._set_transfer()
#             if self.unit.is_worker():
#                 self._set_mine()
#                 self._set_pillage()
#                 self._set_build_city()

#         return self.actions


# class CityPerformance:
#     """Perform citytile object with his posible actions
#     """

#     def __init__(
#         self, 
#         tiles_collection: TilesCollection, 
#         states_collection: StatesCollectionsCollection, 
#         citytile: CityTile
#         ) -> None:
#         self.citytile = citytile
#         self.tiles_collection = tiles_collection
#         self.states_collection = states_collection
#         self.__can_build = None
#         self.actions = {'obj': citytile}

#     @property
#     def _can_build(self) -> bool:
#         """Set citytile can build
#         """
#         if self.__can_build is None:
#             self.__can_build = bool(
#                 len(self.tiles_collection.player_units) - len(self.tiles_collection.player_cities)
#                 )
            
#         return self.__can_build    

#     def _set_research(self) -> None:
#         """Set citytile can research
#         """
#         if not self.tiles_collection.player.researched_uranium():
#             self.actions['research'] = None

#     def _set_build(self) -> None:
#         """Set citytile can build carts or workers
        
#         City cant build units if citytiles == units, owned by player
#         """
#         if self._can_build:
#             self.actions['build_worker'] = None
#             self.actions['build_cart'] = None

#     def get_actions(self) -> dict:
#         """Set all possible actions

#         Returns:
#             dict: object and his posible actions
#         """
#         self.actions['c_pass'] = None
#         if self.citytile.can_act():
#             self._set_research()
#             self._set_build()

#         return self.actions

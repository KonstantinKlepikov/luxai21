from lux.game import Game
from lux.game_objects import Player
from lux.game_objects import Unit, City, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
from bots.utility import (
    UnicPos, GameObjects, GameActiveObject, MissionsState,
    Coord, CrossGameScore, AD
)
import os, sys
from typing import List, Tuple, Union, Dict, Set, Iterable
from collections import ChainMap
from functools import cached_property
from itertools import chain

if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


class SubGameSpace:
    """Define shared data, useed for many games
    """
    
    def __init__(self) -> None:
        # This parametr defines the game number in a series 
        # of train games with the same individual
        self.game_num: int = -1
        # dict where key is a game_num and value is a that game scouring
        self.cross_game_score: CrossGameScore = {}


class GameSpace:
    """Statement game_space for transition to subsequent turns
    """
    
    def __init__(self) -> None:
        self.map_cells: List[Cell] = None
        self.map_cells_pos: List[Position] = None
        self.map_cells_pos_unic: UnicPos = None

        self.missions_state: MissionsState = {}
        self.adj_coord_unic: Set(Coord) = set()
        self.adj_stack: ChainMap = ChainMap()
        
        self.resources: List[Cell] = None
        self.woods: List[Cell] = None
        self.coals: List[Cell] = None
        self.uraniums: List[Cell] = None

        self.resources_pos: List[Position] = None
        # self.woods_pos: List[Position] = None
        # self.coals_pos: List[Position] = None
        # self.uraniums_pos: List[Position] = None

    def _set_res_types(self, game_state: Game, seq: List[Position]) -> None:
        """Set sequence of all resource types
        """
        resources = []
        resources_pos = []
        woods = []
        coals = []
        uraniums = []
        for pos in seq:
            cell = game_state.map.get_cell_by_pos(pos)
            if cell.has_resource():
                resources.append(cell)
                resources_pos.append(pos)
                if cell.resource.type == cs.RESOURCE_TYPES.WOOD:
                    woods.append(cell)
                elif cell.resource.type == cs.RESOURCE_TYPES.COAL:
                    coals.append(cell)
                elif cell.resource.type == cs.RESOURCE_TYPES.URANIUM:
                    uraniums.append(cell)
        self.resources = resources
        self.resources_pos = resources_pos
        self.woods = woods
        self.coals = coals
        self.uraniums = uraniums

    def set_map_statements(self, game_state: Game) -> None:
        """Set map cells and positions
        """
        if game_state.turn == 0:
            self.map_cells = [cell for row in game_state.map.map for cell in row]
            self.map_cells_pos = [cell.pos for cell in self.map_cells]
            self.map_cells_pos_unic: UnicPos = AD[game_state.map_height]['unic_pos']
            self._set_res_types(game_state=game_state, seq=self.map_cells_pos)
        else:
            self.map_cells = [game_state.map.get_cell_by_pos(pos) for pos in self.map_cells_pos]
            self._set_res_types(game_state=game_state, seq=self.resources_pos)


class TilesCollection:
    """Get massive of tiles"""

    def __init__(
        self,
        game_state: Game,
        game_space: GameSpace,
        player: Player,
        opponent: Player
        ) -> None:
        self.game_state = game_state
        self.game_space = game_space
        self.player = player
        self.opponent = opponent

        self.player_units = player.units
        self.opponent_units = opponent.units
        self.build_units_counter = 0
        
    def _pos(self, seq: GameObjects) -> List[Position]:
        """Get sequence of positions

        Args:
            seq (GameObjects): sequence of objects

        Returns:
            List[Position]: list of Positions objects
        """
        return [cell.pos for cell in seq]
    
    def _unic_pos(self, seq: List[Position]) -> UnicPos:
        """Get sequence of unic tuples of coordinates

        Args:
            seq (List[Position]): sequence of positions

        Returns:
            UnicPos: set of tupples
        """
        return {(pos.x, pos.y) for pos in seq}
    
    def _unit_ids(self, seq: List[GameActiveObject]) -> List[str]:
        """Get sequence of unit id-s

        Args:
            seq (GameObjects): sequence of objects

        Returns:
            List[str]: list of ids
        """
        return [cell.id for cell in seq]
    
    def _city_ids(self, seq: List[City]) -> List[str]:
        """Get sequence of city id-s

        Args:
            seq (GameObjects): sequence of objects

        Returns:
            List[str]: list of ids
        """
        return [cell.cityid for cell in seq]

    def cities_can_build(self) -> bool:
        """Cititiles can build

        Returns:
            bool: 
        """
        return (self.city_units_diff - self.build_units_counter) > 0

    @cached_property
    def player_units_pos(self) -> Iterable[Position]:
        """
        Returns positions of all Player's units.

        Returns:
            List[Position]: Positions of the Units.
        """
        return chain(self.player_carts_pos, self.player_workers_pos)
    
    @cached_property
    def player_workers(self) -> List[Unit]:
        """
        Returns Player's workers.

        Returns:
            List[Unit]: Units objects.
        """
        return [unit for unit in self.player_units if unit.is_worker()]

    @cached_property
    def player_workers_pos(self) -> List[Position]:
        """
        Returns Player's workers positions.

        Returns:
            List[Position]: Positions of the workers.
        """
        return self._pos(self.player_workers)
    
    @cached_property
    def player_carts(self) -> List[Unit]:
        """
        Returns Player's carts.

        Returns:
            List[Unit]: Units objects.
        """
        return [unit for unit in self.player_units if unit.is_cart()]
    
    @cached_property
    def player_carts_pos(self) -> List[Position]:
        """
        Returns Player's carts positions.

        Returns:
            List[Position]: Positions of the carts.
        """
        return self._pos(self.player_carts)
    
    @cached_property
    def player_cities(self) -> List[City]:
        """
        Returns Player's Cities.

        Returns:
            List[City]: Cities objects.
        """
        return list(self.player.cities.values())
    
    @cached_property
    def player_citytiles(self) -> List[CityTile]:
        """
        Returns Player's CityTiles.

        Returns:
            List[CityTile]: CityTiles objects.
        """
        citytiles = []
        for city in self.player_cities:
            citytiles = citytiles + city.citytiles
        return citytiles
    
    @cached_property
    def player_citytiles_pos(self) -> List[Position]:
        """
        Returns Player's CityTiles positions.

        Returns:
            List[Position]: Positions of the CityTiles.
        """
        return self._pos(self.player_citytiles)
    
    @cached_property
    def player_own(self) -> Iterable[Union[Unit, CityTile]]:
        """
        Returns all objects owned by Player.

        Returns:
            Iterable[Unit, CityTile]: Player's Unit or CityTile.
        """
        return chain(self.player_units, self.player_citytiles)
    
    @cached_property
    def player_own_pos(self) -> Iterable[Position]:
        """
        Returns positions where Player's Units and CityTiles are located.

        Returns:
            Iterable[Position]: Positions of Units or CityTiles.
        """
        return chain(self.player_units_pos, self.player_citytiles_pos)
    
    @cached_property
    def opponent_units_pos(self) -> Iterable[Position]:
        """
        Returns positions of all Opponent's units.

        Returns:
            Iterable[Position]: Positions of the Units.
        """
        return chain(self.opponent_carts_pos, self.opponent_workers_pos)
    
    @cached_property
    def opponent_workers(self) -> List[Unit]:
        """
        Returns Opponent's workers.

        Returns:
            List[Unit]: Units.
        """
        return [unit for unit in self.opponent_units if unit.is_worker()]
    
    @cached_property
    def opponent_workers_pos(self) -> List[Position]:
        """
        Returns Opponent's workers positions.

        Returns:
            List[Position]: Positions of the workers.
        """
        return self._pos(self.opponent_workers)
    
    @cached_property
    def opponent_carts(self) -> List[Unit]:
        """
        Returns Opponent's carts.

        Returns:
            List[Unit]: Units.
        """
        return [unit for unit in self.opponent_units if unit.is_cart()]
    
    @cached_property
    def opponent_carts_pos(self) -> List[Position]:
        """
        Returns Opponent's carts positions.

        Returns:
            List[Position]: Positions of the carts.
        """
        return self._pos(self.opponent_carts)
    
    @cached_property
    def opponent_cities(self) -> List[City]:
        """
        Returns Opponent's Cities.

        Returns:
            List[City]: Cities.
        """
        return list(self.opponent.cities.values())
    
    @cached_property
    def opponent_citytiles(self) -> List[CityTile]:
        """
        Returns Opponent's CityTiles.

        Returns:
            List[CityTile]: CityTiles.
        """
        citytiles = []
        for city in self.opponent_cities:
            citytiles = citytiles + city.citytiles
        return citytiles
    
    @cached_property
    def opponent_citytiles_pos(self) -> List[Position]:
        """
        Returns Opponent's CityTiles positions.

        Returns:
            List[Position]: Positions of the CityTiles.
        """
        return self._pos(self.opponent_citytiles)
    
    @cached_property
    def opponent_own(self) -> Iterable[Union[Unit, CityTile]]:
        """
        Returns all objects owned by Opponent.

        Returns:
            Iterable[Unit, CityTile]: Opponent's objects with type Unit or CityTile.
        """
        return chain(self.opponent_units, self.opponent_citytiles)
    
    @cached_property
    def opponent_own_pos(self) -> Iterable[Position]:
        """
        Returns positions where Opponent's Units and CityTiles are located.

        Returns:
            Iterable[Position]: Position of Units or CityTiles.
        """
        return chain(self.opponent_units_pos, self.opponent_citytiles_pos)
    
    @cached_property
    def own(self) -> Iterable[Union[Unit, CityTile]]:
        """
        Returns all objects owned by Player and Opponent.

        Returns:
            Iterable[Unit, CityTile]: objects with type Unit or CityTile.
        """
        return chain(self.player_own, self.opponent_own)
    
    @cached_property
    def own_pos(self) -> Iterable[Position]:
        """
        Returns positions where Player's and Opponent's Units and CityTiles are located.

        Returns:
            Iterable[Position]: Positions Units or CityTiles.
        """
        return chain(self.player_own_pos, self.opponent_own_pos)
    
    @cached_property
    def own_pos_unic(self) -> UnicPos:
        """Returns unic coordinates, owned by player or opponent

        Returns:
            UnicPos: coordinate tuples
        """
        return self._unic_pos(self.own_pos)
    
    @cached_property
    def empty_pos_unic(self) -> UnicPos:
        """Returns unic coordinates of unowned cells

        Returns:
            UnicPos: coordinate tuples
        """
        return self.game_space.map_cells_pos_unic - self.own_pos_unic
    
    @cached_property
    def empty_pos(self) -> List[Position]:
        """
        Returns Position of all empty Cell objects on game map.

        Returns:
            List[Position]: Positions of the empty Cells;
        """
        return [Position(coor[0], coor[1]) for coor in self.empty_pos_unic]
    
    @cached_property
    def workers(self) -> Iterable[Unit]:
        """
        Returns Player's and Opponent's workers.

        Returns:
            Iterable[Unit]: Units.
        """
        return chain(self.player_workers, self.opponent_workers)

    @cached_property
    def workers_pos(self) -> Iterable[Position]:
        """
        Returns Player's and Opponent's workers positions.

        Returns:
            Iterable[Position]: Positions of the workers.
        """
        return chain(self.player_workers_pos, self.opponent_workers_pos)
    
    @cached_property
    def carts(self) -> Iterable[Unit]:
        """
        Returns Player's and Opponent's carts.

        Returns:
            Iterable[Unit]: Units.
        """
        return chain(self.player_carts, self.opponent_carts)
    
    @cached_property
    def carts_pos(self) -> Iterable[Position]:
        """
        Returns Player's and Opponent's carts positions.

        Returns:
            Iterable[Position]: Positions of the carts.
        """
        return chain(self.player_carts_pos, self.opponent_carts_pos)
    
    @cached_property
    def cities(self) -> Iterable[City]:
        """
        Returns Player's and Opponent's Cities.

        Returns:
            Iterable[City]: Cities.
        """
        return chain(self.player_cities, self.opponent_cities)
    
    @cached_property
    def citytiles(self) -> Iterable[CityTile]:
        """
        Returns Player's and Opponent's CityTiles.

        Returns:
            Iterable[CityTile]: CityTiles.
        """
        return chain(self.player_citytiles, self.opponent_citytiles)
    
    @cached_property
    def citytiles_pos(self) -> Iterable[Position]:
        """
        Returns Player's and Opponent's CityTiles positions.

        Returns:
            Iterable[Position]: Positions of the CityTiles.
        """
        return chain(self.player_citytiles_pos, self.opponent_citytiles_pos)
    
    @cached_property
    def roads(self) -> List[Cell]:
        """
        Returns Cells with road on game map.

        Returns:
            List[Cell]: Cells.
        """
        return [cell for cell in self.game_space.map_cells if cell.road]
    
    @cached_property
    def roads_pos(self) -> List[Position]:
        """
        Returns positions of tiles with road.

        Returns:
            List[Position]: Positions of the tile.
        """
        return self._pos(self.roads)
    
    @cached_property
    def city_units_diff(self) -> int:
        """Positive difference

        Returns:
            int: difference player cititiles and units - 0 or more
        """
        diff = len(self.player_citytiles) - len(self.player_units)
        return diff if diff >= 0 else 0


class TileState:
    """Get tile statement
    """

    def __init__(self, tiles: TilesCollection, pos: Position) -> None:
        self.tiles = tiles
        self.pos = pos
        self.map_width = tiles.game_state.map_width
        self.map_height = tiles.game_state.map_height
        self.cell = tiles.game_state.map.get_cell_by_pos(pos)

        self.player_worker_object: Union[Unit, None] = None
        self.player_cart_object: Union[Unit, None] = None
        self.opponent_worker_object: Union[Unit, None] = None
        self.opponent_cart_object: Union[Unit, None] = None

    @cached_property
    def is_owned_by_player(self) -> bool:
        """Is owned by player
        """
        return self.cell.pos in self.tiles.player_own_pos
    
    @cached_property
    def is_owned_by_opponent(self) -> bool:
        """Is owned by opponent
        """
        return self.cell.pos in self.tiles.opponent_own_pos

    @cached_property
    def is_owned(self) -> bool:
        """Is owned by any
        """
        if self.is_owned_by_player or self.is_owned_by_opponent:
            return True
        else:
            return False

    @cached_property
    def is_resource(self) -> bool:
        """Is tile resource
        """
        return self.cell.has_resource()

    @cached_property
    def is_wood(self) -> bool:
        """Is tile wood
        """
        return self.cell in self.tiles.game_space.woods

    @cached_property
    def is_coal(self) -> bool:
        """Is tile wood
        """
        return self.cell in self.tiles.game_space.coals

    @cached_property
    def is_uranium(self) -> bool:
        """Is tile wood
        """
        return self.cell in self.tiles.game_space.uraniums

    @cached_property
    def is_road(self) -> bool:
        """Is tile Road
        """
        return self.cell in self.tiles.roads

    @cached_property
    def is_city(self) -> bool:
        """Is tile city
        """
        return bool(self.cell.citytile)

    @cached_property
    def is_worker(self) -> bool:
        """Is tile worker
        """
        x, y = self.cell.pos
        return Position(x, y) in self.tiles.workers_pos

    @cached_property
    def is_cart(self) -> bool:
        """Is tile cart
        """
        x, y = self.cell.pos
        return Position(x, y) in self.tiles.carts_pos

    @cached_property
    def is_empty(self) -> bool:
        """Is tile empty
        """
        return self.cell.pos in self.tiles.empty_pos

    @cached_property
    def adjacence_unic_pos(self) -> UnicPos:
        """Adjaced coordinates

        Returns:
            UnicPos: coordinate tuples
        """
        return set(AD[self.map_width]['adjacence'][(self.pos.x, self.pos.y)].keys())

    @cached_property
    def adjacence_dir(self) -> Dict[str, Position]:
        """Calculate dict, where keys are directions, values - positions of adjacent tiles

        Returns:
            Dict[str, Position]: positions and directions
        """
        return {
                val: Position(key[0], key[1])
                for key, val in AD[self.map_width]['adjacence'][(self.pos.x, self.pos.y)].items()
                }

    @cached_property
    def adjacent_pos(self) -> List[Position]:
        """Calculate positions of adjacent tiles

        Returns:
            List[Position]: positions
        """
        return list(self.adjacence_dir.values())

    @cached_property
    def adjacent_dir_unic_pos(self) -> Dict[str, Tuple[int]]:
        """Calculate dict, where keys are directions, values - tuples of x, y positions

        Returns:
            Dict(str, Tuple[int]): directions and tuples with coordinates
        """
        return {
                val: key
                for key, val in AD[self.map_width]['adjacence'][(self.pos.x, self.pos.y)].items()
                }


class TileStatesCollection:
    """Get statement matrix across all tiles
    """

    def __init__(self, game_state: Game, tiles: TilesCollection) -> None:
        self.states_map = [[None for _ in range(game_state.map.width)] for _ in range(game_state.map.height)]
        self.tiles = tiles
        self.turn = game_state.turn

    def get_state(self, pos: Position) -> TileState:
        """Get TileState of any tile by position

        Args:
            pos (Position): position object

        Returns:
            [type]: TileState object for given position
        """
        if self.states_map[pos.x][pos.y] is None:
            self.states_map[pos.x][pos.y] = TileState(tiles=self.tiles, pos=pos)
        return self.states_map[pos.x][pos.y]

    @cached_property
    def player_active_obj_to_state(self) -> None:
        """init all player unit objects in collection of tile states
        """
        carts = self.tiles.player_carts
        workers = self.tiles.player_workers
        for worker in workers:
            tile_state = self.get_state(worker.pos)
            tile_state.player_worker_object = worker
        for cart in carts:
            tile_state = self.get_state(cart.pos)
            tile_state.player_cart_object = cart

    @cached_property
    def opponent_active_obj_to_state(self) -> None:
        """init all opponent unit objects in collection of tile states
        """
        carts = self.tiles.opponent_carts
        workers = self.tiles.opponent_workers
        for worker in workers:
            tile_state = self.get_state(worker.pos)
            tile_state.opponent_worker_object = worker
        for cart in carts:
            tile_state = self.get_state(cart.pos)
            tile_state.opponent_cart_object = cart


class ContestedTilesCollection:
    """Get tiles collections, contested by player units
    """

    def __init__(
        self,
        tiles: TilesCollection,
        states: TileStatesCollection
        ) -> None:
        self.tiles = tiles
        self.states = states
    
    @cached_property
    def tiles_to_move(self) -> UnicPos:
        """All adjacent to player units tiles

        Returns:
            UnicPos: sequence of tiles positions
        """
        coord = set()
        for pos in self.tiles.player_units_pos:
            tile_state = self.states.get_state(pos=pos).adjacence_unic_pos
            coord.update(tile_state)
        return coord

    @cached_property
    def tiles_free(self) -> UnicPos:
        """Available tiles, exclude opponent cities and units

        Returns:
            UnicPos: sequence of tiles positions
        """
        coords = self.tiles_to_move.copy()
        for coord in self.tiles_to_move:
            tile_state = self.states.get_state(pos=Position(coord[0], coord[1]))
            if tile_state.is_owned_by_opponent:
                coords.discard(coord)
        return coords


class AdjacentToResourceCollection:
    """Calculate adjacence to resourse
    """
    
    def __init__(
        self,
        tiles: TilesCollection,
        states: TileStatesCollection,
        ) -> None:
        self.tiles = tiles
        self.states = states
        self.adj_coord_unic: Set(Coord) = None
        self.__empty_adjacent_any_pos = None
        self.__empty_adjacent_wood_pos = None
        self.__empty_adjacent_wood_coal_pos = None
        
    def _set_empty_adjacent_res_pos(self) -> None:
        any_ = []
        wood = []
        wood_coal = []
        for coord in self.adj_coord_unic:
            pos = Position(coord[0], coord[1])
            state = self.states.get_state(pos)
            if state.is_empty:
                any_.append(pos)
                if state.is_wood:
                    wood.append(pos)
                if self.tiles.player.researched_coal() and (state.is_wood or state.is_coal):
                    wood_coal.append(pos)
        self.__empty_adjacent_any_pos = any_
        self.__empty_adjacent_wood_pos = wood
        self.__empty_adjacent_wood_coal_pos = wood_coal
    
    @property
    def empty_adjacent_any_pos(self) -> List[Position]:
        if self.__empty_adjacent_any_pos is None:
            self._set_empty_adjacent_res_pos()
        return self.__empty_adjacent_any_pos
    
    @property
    def empty_adjacent_wood_pos(self) -> List[Position]:
        if self.__empty_adjacent_wood_pos is None:
            self._set_empty_adjacent_res_pos()
        return self.__empty_adjacent_wood_pos
    
    @property
    def empty_adjacent_wood_coal_pos(self) -> List[Position]:
        if self.__empty_adjacent_wood_coal_pos is None:
            self._set_empty_adjacent_res_pos()
        return self.__empty_adjacent_wood_coal_pos


class TurnSpace:
    """Collected game statements
    """
    
    def __init__(
        self,
        game_state: Game,
        game_space: GameSpace,
        player: Player,
        opponent: Player
        ) -> None:
        self.game_space = game_space
        self.tiles = TilesCollection(
            game_state=game_state,
            game_space=game_space,
            player=player,
            opponent=opponent
            )
        self.states = TileStatesCollection(
            game_state=game_state,
            tiles=self.tiles
        )
        self.contested = ContestedTilesCollection(
            tiles=self.tiles,
            states=self.states
            )
        self.adjcollection = AdjacentToResourceCollection(
            tiles=self.tiles,
            states=self.states
        )

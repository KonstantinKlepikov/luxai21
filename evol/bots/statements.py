from lux.game import Game
from lux.game_objects import Player
from lux.game_objects import Unit, City, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
from bots.utility import (
    UnicPos, GameObjects, GameActiveObject, MissionsState,
    Coord, AD
)
import os, sys
from typing import List, Tuple, Union, Dict, Set
from collections import ChainMap

if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


class TransitionStates:
    """Statement transition to next turn"""
    
    def __init__(self) -> None:
        self.missions_state: MissionsState = {}
        self.adj_coord_unic: Set(Coord) = set()
        self.adj_stack: ChainMap = ChainMap()


class TilesCollection:
    """Get massive of tiles"""

    def __init__(self, game_state: Game, player: Player, opponent: Player) -> None:
        self.game_state = game_state
        self.player = player
        self.opponent = opponent

        self.__map_cells = None
        self.__map_cells_pos = None
        self.map_cells_pos_unic: UnicPos = AD[game_state.map_height]['unic_pos']

        self.player_units = player.units
        self.__player_units_pos = None
        self.__player_workers = None
        self.__player_workers_pos = None
        self.__player_workers_id = None
        self.__player_carts = None
        self.__player_carts_pos = None
        self.__player_carts_id = None
        self.__player_cities = None
        self.__player_citytiles = None
        self.__player_citytiles_pos = None
        self.__player_cities_id = None
        self.__player_own = None
        self.__player_own_pos = None

        self.opponent_units = opponent.units
        self.__opponent_units_pos = None
        self.__opponent_workers = None
        self.__opponent_workers_pos = None
        self.__opponent_workers_id = None
        self.__opponent_carts = None
        self.__opponent_carts_pos = None
        self.__opponent_carts_id = None
        self.__opponent_cities = None
        self.__opponent_citytiles = None
        self.__opponent_citytiles_pos = None
        self.__opponent_cities_id = None
        self.__opponent_own = None
        self.__opponent_own_pos = None

        self.__own = None
        self.__own_pos = None
        self.__own_pos_unic = None
        self.__empty_pos = None
        self.__empty_pos_unic = None

        self.__workers = None
        self.__workers_pos = None
        self.__workers_id = None
        self.__carts = None
        self.__carts_pos = None
        self.__carts_id = None

        self.__cities = None
        self.__citytiles = None
        self.__citytiles_pos = None
        self.__cities_id = None

        self.__roads = None
        self.__roads_pos = None

        self.__resources = None
        self.__resources_pos = None
        self.__woods = None
        self.__woods_pos = None
        self.__coals = None
        self.__coals_pos = None
        self.__uraniums = None
        self.__uraniums_pos = None
        
        self.__city_units_diff = None
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
    
    def _set_res_types(self) -> None:
        """Set sequence of all resource types
        """
        resources = []
        woods = []
        coals = []
        uraniums = []
        for cell in self.map_cells:
            if cell.has_resource():
                resources.append(cell)
                if cell.resource.type == cs.RESOURCE_TYPES.WOOD:
                    woods.append(cell)
                elif cell.resource.type == cs.RESOURCE_TYPES.COAL:
                    coals.append(cell)
                elif cell.resource.type == cs.RESOURCE_TYPES.URANIUM:
                    uraniums.append(cell)
        self.__resources = resources
        self.__woods = woods
        self.__coals = coals
        self.__uraniums = uraniums
        
    def cities_can_build(self) -> bool:
        """Cititiles can build

        Returns:
            bool: 
        """
        return (self.city_units_diff - self.build_units_counter) > 0

    @property
    def map_cells(self) -> List[Cell]:
        """
        Returns cells object of map.

        Args:
        Returns:
            List[Cells]: game_map.Cell object. Every Cell contain information about:
                - citytile (game_objects.CityTile): object for the CityTile;
                - pos (Position): game_map.Position object for coordinate of the tile (x: int, y: int);
                - resource (game_map.Resource {amount: int, type: str}): information about resource on the tile;
                - road (int): level of road on the tile.
        """
        if self.__map_cells is None:
            self.__map_cells = [cell for row in self.game_state.map.map for cell in row]
        return self.__map_cells
    
    @property
    def map_cells_pos(self) -> List[Position]:
        """
        Returns positions of all cells.

        Args:
        Returns:
            List[Position]: game_map.Position object
        """
        if self.__map_cells_pos is None:
            self.__map_cells_pos = self._pos(self.map_cells)
        return self.__map_cells_pos

    # player
    @property
    def player_units_pos(self) -> List[Position]:
        """
        Returns positions of all Player's units.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the Unit (x: int, y: int).
        """
        if self.__player_units_pos is None:
            self.__player_units_pos = self.player_carts_pos + self.player_workers_pos
        return self.__player_units_pos

    @property
    def player_workers(self) -> List[Unit]:
        """
        Returns list of Player's workers.

        Args:
        Returns:
            List[Unit]: game_object.Unit object. Every Unit contain information:
                - cargo (Cargo): Cargo object | Wood (int): value, Coal (int): value, Uranium (int): value;
                - cooldown (float): Cooldown time for worker;
                - id (str): unique ID for Unit in form u_1;
                - pos (Position): game_map.Position object for coordinate of the worker (x: int, y: int);
                - team (int): team = 0 for Player;
                - type (int): type = 0 for worker.
        """
        if self.__player_workers is None:
            self.__player_workers = [unit for unit in self.player_units if unit.is_worker()]
        return self.__player_workers

    @property
    def player_workers_pos(self) -> List[Position]:
        """
        Returns list of Player's workers positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the worker (x: int, y: int).
        """
        if self.__player_workers_pos is None:
            self.__player_workers_pos = self._pos(self.player_workers)
        return self.__player_workers_pos

    @property
    def player_carts(self) -> List[Unit]:
        """
        Returns list of Player's carts.

        Args:
        Returns:
            List[Unit]: game_object.Unit object. Every Unit contain information:
                - cargo (Cargo): Cargo object | Wood (int): value, Coal (int): value, Uranium (int): value;
                - cooldown (float): Cooldown time for worker;
                - id (str): unique ID for Unit in form 'u_1';
                - pos (Position): game_map.Position object for coordinates of the cart (x: int, y: int);
                - team (int): team = 0 for Player;
                - type (int): type = 1 for cart.
        """
        if self.__player_carts is None:
            self.__player_carts = [unit for unit in self.player_units if unit.is_cart()]
        return self.__player_carts

    @property
    def player_carts_pos(self) -> List[Position]:
        """
        Returns list of Player's carts positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinates of the cart (x: int, y: int).
        """
        if self.__player_carts_pos is None:
            self.__player_carts_pos = self._pos(self.player_carts)
        return self.__player_carts_pos

    @property
    def player_cities(self) -> List[City]:
        """
        Returns list of Player's Cities.

        Args:
        Returns:
            List[City]: game_object.City object. Every City object contains information:
                - cityid (str): Unique ID for the City in form 'c_1';
                - citytiles (List[CityTile]): game_object.CityTile objects forming current City;
                - fuel (float): Quantity of fuel kept in current City;
                - light_upkeep (float): Quantity of fuel required every night for warming;
                - team (int): team = 0 for Player.
        """
        if self.__player_cities is None:
            self.__player_cities = list(self.player.cities.values())
        return self.__player_cities

    @property
    def player_citytiles(self) -> List[CityTile]:
        """
        Returns list of Player's CityTiles.

        Args:
        Returns:
            List[CityTile]: game_object.CityTile object. Each CityTile object contain information:
            - cityid (srt): Unique ID for the City in form 'c_1';
            - cooldown (float): Cooldown time for current CityTile;
            - pos (Position): game_map.Position object for coordinate of the CityTile (x: int, y: int);
            - team (int): team = 0 for Player.
        """
        if self.__player_citytiles is None:
            citytiles = []
            for city in self.player_cities:
                citytiles = citytiles + city.citytiles
            self.__player_citytiles = citytiles
        return self.__player_citytiles

    @property
    def player_citytiles_pos(self) -> List[Position]:
        """
        Returns list of Player's CityTiles positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the CityTile (x: int, y: int).
        """
        if self.__player_citytiles_pos is None:
            self.__player_citytiles_pos = self._pos(self.player_citytiles)
        return self.__player_citytiles_pos

    @property
    def player_own(self) -> List[Union[Unit, CityTile]]:
        """
        Returns list of all objects owned by Player.

        Args:
        Returns:
            List[Unit, CityTile]: Full list of Player's objects with type Unit or CityTile.
        """
        if self.__player_own is None:
            self.__player_own = self.player_units + self.player_citytiles
        return self.__player_own

    @property
    def player_own_pos(self) -> List[Position]:
        """
        Returns list of positions where Player's Units and CityTiles are located.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Unit or CityTile (x: int, y: int).
        """
        if self.__player_own_pos is None:
            self.__player_own_pos = self.player_units_pos + self.player_citytiles_pos
        return self.__player_own_pos

    # opponent
    @property
    def opponent_units_pos(self) -> List[Position]:
        """
        Returns positions of all Opponent's units.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the Unit (x: int, y: int).
        """
        if self.__opponent_units_pos is None:
            self.__opponent_units_pos = self.opponent_carts_pos + self.opponent_workers_pos
        return self.__opponent_units_pos

    @property
    def opponent_workers(self) -> List[Unit]:
        """
        Returns list of Opponent's workers.

        Args:
        Returns:
            List[Unit]: game_object.Unit object. Every Unit contain information:
                - cargo (Cargo): Cargo object | Wood (int): value, Coal (int): value, Uranium (int): value;
                - cooldown (float): Cooldown time for worker;
                - id (str): unique ID for Unit in form u_1;
                - pos (Position): game_map.Position object for coordinate of the worker (x: int, y: int);
                - team (int): team = 1 for Opponent;
                - type (int): type = 0 for worker.
        """
        if self.__opponent_workers is None:
            self.__opponent_workers = [unit for unit in self.opponent_units if unit.is_worker()]
        return self.__opponent_workers

    @property
    def opponent_workers_pos(self) -> List[Position]:
        """
        Returns list of Opponent's workers positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the worker (x: int, y: int).
        """
        if self.__opponent_workers_pos is None:
            self.__opponent_workers_pos = self._pos(self.opponent_workers)
        return self.__opponent_workers_pos

    @property
    def opponent_carts(self) -> List[Unit]:
        """
        Returns list of Opponent's carts.

        Args:
        Returns:
            List[Unit]: game_object.Unit object. Every Unit contain information:
                - cargo (Cargo): Cargo object | Wood (int): value, Coal (int): value, Uranium (int): value;
                - cooldown (float): Cooldown time for worker;
                - id (str): unique ID for Unit in form 'u_1';
                - pos (Position): game_map.Position object for coordinates of the cart (x: int, y: int);
                - team (int): team = 1 for Opponent;
                - type (int): type = 1 for cart.
        """
        if self.__opponent_carts is None:
            self.__opponent_carts = [unit for unit in self.opponent_units if unit.is_cart()]
        return self.__opponent_carts

    @property
    def opponent_carts_pos(self) -> List[Position]:
        """
        Returns list of Opponent's carts positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinates of the cart (x: int, y: int).
        """
        if self.__opponent_carts_pos is None:
            self.__opponent_carts_pos = self._pos(self.opponent_carts)
        return self.__opponent_carts_pos

    @property
    def opponent_cities(self) -> List[City]:
        """
        Returns list of Opponent's Cities.

        Args:
        Returns:
            List[City]: game_object.City object. Every City object contains information:
                - cityid (str): Unique ID for the City in form 'c_1';
                - citytiles (List[CityTile]): game_object.CityTile objects forming current City;
                - fuel (float): Quantity of fuel kept in current City;
                - light_upkeep (float): Quantity of fuel required every night for warming;
                - team (int): team = 1 for Opponent.
        """
        if self.__opponent_cities is None:
            self.__opponent_cities = list(self.opponent.cities.values())
        return self.__opponent_cities

    @property
    def opponent_citytiles(self) -> List[CityTile]:
        """
        Returns list of Opponent's CityTiles.

        Args:
        Returns:
            List[CityTile]: game_object.CityTile object. Each CityTile object contain information:
            - cityid (srt): Unique ID for the City in form 'c_1';
            - cooldown (float): Cooldown time for current CityTile;
            - pos (Position): game_map.Position object for coordinate of the CityTile (x: int, y: int);
            - team (int): team = 1 for Opponent.
        """
        if self.__opponent_citytiles is None:
            citytiles = []
            for city in self.opponent_cities:
                citytiles = citytiles + city.citytiles
            self.__opponent_citytiles = citytiles
        return self.__opponent_citytiles

    @property
    def opponent_citytiles_pos(self) -> List[Position]:
        """
        Returns list of Opponent's CityTiles positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the CityTile (x: int, y: int).
        """
        if self.__opponent_citytiles_pos is None:
            self.__opponent_citytiles_pos = self._pos(self.opponent_citytiles)
        return self.__opponent_citytiles_pos

    @property
    def opponent_own(self) -> List[Union[Unit, CityTile]]:
        """
        Returns list of all objects owned by Opponent.

        Args:
        Returns:
            List[Unit, CityTile]: Full list of Opponent's objects with type Unit or CityTile.
        """
        if self.__opponent_own is None:
            self.__opponent_own = self.opponent_units + self.opponent_citytiles
        return self.__opponent_own

    @property
    def opponent_own_pos(self) -> List[Position]:
        """
        Returns list of positions where Opponent's Units and CityTiles are located.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Unit or CityTile (x: int, y: int).
        """
        if self.__opponent_own_pos is None:
            self.__opponent_own_pos = self.opponent_units_pos + self.opponent_citytiles_pos
        return self.__opponent_own_pos

    # owns
    @property
    def own(self) -> List[Union[Unit, CityTile]]:
        """
        Returns list of all objects owned by Player and Opponent.

        Args:
        Returns:
            List[Unit, CityTile]: Full list of objects with type Unit or CityTile.
        """
        if self.__own is None:
            self.__own = self.player_own + self.opponent_own
        return self.__own

    @property
    def own_pos(self) -> List[Position]:
        """
        Returns list of positions where Player's and Opponent's Units and CityTiles are located.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Unit or CityTile (x: int, y: int).
        """
        if self.__own_pos is None:
            self.__own_pos = self.player_own_pos + self.opponent_own_pos
        return self.__own_pos
    
    @property
    def own_pos_unic(self) -> UnicPos:
        """Returns sequence of unic coordinates, owned by player or opponent

        Returns:
            UnicPos: set of tuples
        """
        if self.__own_pos_unic is None:
            self.__own_pos_unic = self._unic_pos(self.own_pos)
        return self.__own_pos_unic
    
    @property
    def empty_pos_unic(self) -> UnicPos:
        """Returns sequence of unic coordinates of notowned cells

        Returns:
            UnicPos: set of tuples
        """
        if self.__empty_pos_unic is None:
            self.__empty_pos_unic = self.map_cells_pos_unic - self.own_pos_unic
        return self.__empty_pos_unic

    @property
    def empty_pos(self) -> List[Position]:
        """
        Returns list of Position of all empty Cell objects on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the empty Cell (x: int, y: int);
        """
        if self.__empty_pos is None:
            self.__empty_pos = [Position(coor[0], coor[1]) for coor in self.empty_pos_unic]
        return self.__empty_pos

    # units
    @property
    def workers(self) -> List[Unit]:
        """
        Returns list of Player's and Opponent's workers.

        Args:
        Returns:
            List[Unit]: game_object.Unit object. Every Unit contain information:
                - cargo (Cargo): Cargo object | Wood (int): value, Coal (int): value, Uranium (int): value;
                - cooldown (float): Cooldown time for worker;
                - id (str): unique ID for Unit in form u_1;
                - pos (Position): game_map.Position object for coordinate of the worker (x: int, y: int);
                - team (int): team = 0 for Player, team = 1 for Opponent;
                - type (int): type = 0 for worker.
        """
        if self.__workers is None:
            self.__workers = self.player_workers + self.opponent_workers
        return self.__workers

    @property
    def workers_pos(self) -> List[Position]:
        """
        Returns list of Player's and Opponent's workers positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the worker (x: int, y: int).
        """
        if self.__workers_pos is None:
            self.__workers_pos = self.player_workers_pos + self.opponent_workers_pos
        return self.__workers_pos

    @property
    def carts(self) -> List[Unit]:
        """
        Returns list of Player's and Opponent's carts.

        Args:
        Returns:
            List[Unit]: game_object.Unit object. Every Unit contain information:
                - cargo (Cargo): Cargo object | Wood (int): value, Coal (int): value, Uranium (int): value;
                - cooldown (float): Cooldown time for worker;
                - id (str): unique ID for Unit in form 'u_1';
                - pos (Position): game_map.Position object for coordinates of the cart (x: int, y: int);
                - team (int): team = 0 for Player, team = 1 for Opponent;
                - type (int): type = 1 for cart.
        """
        if self.__carts is None:
            self.__carts = self.player_carts + self.opponent_carts
        return self.__carts

    @property
    def carts_pos(self) -> List[Position]:
        """
        Returns list of Player's and Opponent's carts positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinates of the cart (x: int, y: int).
        """
        if self.__carts_pos is None:
            self.__carts_pos = self.player_carts_pos + self.opponent_carts_pos
        return self.__carts_pos

    # city
    @property
    def cities(self) -> List[City]:
        """
        Returns list of Player's and Opponent's Cities.

        Args:
        Returns:
            List[City]: game_object.City object. Every City object contains information:
                - cityid (str): Unique ID for the City in form 'c_1';
                - citytiles (List[CityTile]): game_object.CityTile objects forming current City;
                - fuel (float): Quantity of fuel kept in current City;
                - light_upkeep (float): Quantity of fuel required every night for warming;
                - team (int): team = 0 for Player, team = 1 for Opponent.
        """
        if self.__cities is None:
            self.__cities = self.player_cities + self.opponent_cities
        return self.__cities

    @property
    def citytiles(self) -> List[CityTile]:
        """
        Returns list of Player's and Opponent's CityTiles.

        Args:
        Returns:
            List[CityTile]: game_object.CityTile object. Each CityTile object contain information:
            - cityid (srt): Unique ID for the City in form 'c_1';
            - cooldown (float): Cooldown time for current CityTile;
            - pos (Position): game_map.Position object for coordinate of the CityTile (x: int, y: int);
            - team (int): team = 0 for Player, team = 1 for Opponent.
        """
        if self.__citytiles is None:
            self.__citytiles = self.player_citytiles + self.opponent_citytiles
        return self.__citytiles

    @property
    def citytiles_pos(self) -> List[Position]:
        """
        Returns list of Player's and Opponent's CityTiles positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the CityTile (x: int, y: int).
        """
        if self.__citytiles_pos is None:
            self.__citytiles_pos = self.player_citytiles_pos + self.opponent_citytiles_pos
        return self.__citytiles_pos

    # roads
    @property
    def roads(self) -> List[Cell]:
        """
        Returns list of Cells with road on game map.

        Args:
        Returns:
            List[Cell]: game_map.Cell object. Every Cell contain information about:
                - citytile (CityTile): game_object.CityTile object;
                - pos (Position): game_map.Position object for coordinate of the Cell (x: int, y: int);
                - resource (NoneType): None
                - road (float): level of road on the tile.
        """
        if self.__roads is None:
            self.__roads = [cell for cell in self.map_cells if cell.road]
        return self.__roads

    @property
    def roads_pos(self) -> List[Position]:
        """
        Returns list of positions of tiles with road.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the tile (x: int, y: int).
        """
        if self.__roads_pos is None:
            self.__roads_pos = self._pos(self.roads)
        return self.__roads_pos

    # resources
    @property
    def resources(self) -> List[Cell]:
        """
        Returns list of Cells with resource of any type on game map.

        Args:
        Returns:
            List[Cell]: game_map.Cell object. Every Cell contain information about:
                - citytile (NoneType): None;
                - pos (Position): game_map.Position object for coordinate of the Cell (x: int, y: int);
                - resource (Resource): game_map.Resource object. Contains next info:
                    - amount (int): value of resource;
                    - type (str); 'wood' or 'coal' or 'uranium'
                - road (int): 0.
        """
        if self.__resources is None:
            self._set_res_types()
        return self.__resources

    @property
    def resources_pos(self) -> List[Position]:
        """
        Returns list of positions of all resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the resource (x: int, y: int).
        """
        if self.__resources_pos is None:
            self.__resources_pos = self._pos(self.resources)
        return self.__resources_pos

    @property
    def woods(self) -> List[Cell]:
        """
        Returns list of Cells with wood resource on game map.

        Args:
        Returns:
            List[Cell]: game_map.Cell object. Every Cell contain information about:
                - citytile (NoneType): None;
                - pos (Position): game_map.Position object for coordinate of the Cell (x: int, y: int);
                - resource (Resource): game_map.Resource object. Contains next info:
                    - amount (int): value of resource;
                    - type (str); 'wood'
                - road (int): 0.
        """
        if self.__woods is None:
            self._set_res_types()
        return self.__woods

    @property
    def woods_pos(self) -> List[Position]:
        """
        Returns list of positions of wood resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the wood (x: int, y: int).
        """
        if self.__woods_pos is None:
            self.__woods_pos = self._pos(self.woods)
        return self.__woods_pos

    @property
    def coals(self) -> List[Cell]:
        """
        Returns list of Cells with coal resource on game map.

        Args:
        Returns:
            List[Cell]: game_map.Cell object. Every Cell contain information about:
                - citytile (NoneType): None;
                - pos (Position): game_map.Position object for coordinate of the Cell (x: int, y: int);
                - resource (Resource): game_map.Resource object. Contains next info:
                    - amount (int): value of resource;
                    - type (str); 'coal'
                - road (int): 0.
        """
        if self.__coals is None:
            self._set_res_types()
        return self.__coals

    @property
    def coals_pos(self) -> List[Position]:
        """
        Returns list of positions of coal resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the coal (x: int, y: int).
        """
        if self.__coals_pos is None:
            self.__coals_pos = self._pos(self.coals)
        return self.__coals_pos

    @property
    def uraniums(self) -> List[Cell]:
        """
        Returns list of Cells with uranium resource on game map.

        Args:
        Returns:
            List[Cell]: game_map.Cell object. Every Cell contain information about:
                - citytile (NoneType): None;
                - pos (Position): game_map.Position object for coordinate of the Cell (x: int, y: int);
                - resource (Resource): game_map.Resource object. Contains next info:
                    - amount (int): value of resource;
                    - type (str); 'uranium'
                - road (int): 0.
        """
        if self.__uraniums is None:
            self._set_res_types()
        return self.__uraniums

    @property
    def uraniums_pos(self) -> List[Position]:
        """
        Returns list of positions of uranium resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the uranium (x: int, y: int).
        """
        if self.__uraniums_pos is None:
            self.__uraniums_pos = self._pos(self.uraniums)
        return self.__uraniums_pos

    # identifiers
    @property
    def player_cities_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Player's cities at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'c_1'
        """
        if self.__player_cities_id is None:
            self.__player_cities_id = self._city_ids(self.player_cities)
        return self.__player_cities_id

    @property
    def player_workers_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Player's workers at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'u_1'
        """
        if self.__player_workers_id is None:
            self.__player_workers_id = self._unit_ids(self.player_workers)
        return self.__player_workers_id

    @property
    def player_carts_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Player's carts at a game map.

        Args:
        Returns:
            List[str]: cart identifier in form 'u_1'
        """
        if self.__player_carts_id is None:
            self.__player_carts_id = self._unit_ids(self.player_carts)
        return self.__player_carts_id

    @property
    def opponent_cities_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Opponent's cities at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'c_1'
        """
        if self.__opponent_cities_id is None:
            self.__opponent_cities_id = self._city_ids(self.opponent_cities)
        return self.__opponent_cities_id
    
    @property
    def opponent_workers_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Opponent's workers at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'u_1'
        """
        if self.__opponent_workers_id is None:
            self.__opponent_workers_id = self._unit_ids(self.opponent_workers)
        return self.__opponent_workers_id
    
    @property
    def opponent_carts_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Opponent's carts at a game map.

        Args:
        Returns:
            List[str]: cart identifier in form 'u_1'
        """
        if self.__opponent_carts_id is None:
            self.__opponent_carts_id = self._unit_ids(self.opponent_carts)
        return self.__opponent_carts_id

    @property
    def cities_id(self) -> List[str]:
        """
        Returns list of unique identifiers of all cities at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'c_1'
        """
        if self.__cities_id is None:
            self.__cities_id = self.player_cities_id + self.opponent_cities_id
        return self.__cities_id

    @property
    def workers_id(self) -> List[str]:
        """
        Returns list of unique identifiers of all workers at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'u_1'
        """
        if self.__workers_id is None:
            self.__workers_id = self.player_workers_id + self.opponent_workers_id
        return self.__workers_id

    @property
    def carts_id(self) -> List[str]:
        """
        Returns list of unique identifiers of all carts at a game map.

        Args:
        Returns:
            List[str]: cart identifier in form 'u_1'
        """
        if self.__carts_id is None:
            self.__carts_id = self.player_carts_id + self.opponent_carts_id
        return self.__carts_id
    
    @property
    def city_units_diff(self) -> int:
        """Positive difference

        Returns:
            int: difference player cititiles and units - 0 or more
        """
        if self.__city_units_diff is None:
            diff = len(self.player_citytiles) - len(self.player_units)
            self.__city_units_diff = diff if diff >= 0 else 0
        return self.__city_units_diff


class TileState:
    """Get tile statement
    """

    def __init__(self, tiles: TilesCollection, pos: Position) -> None:
        self.tiles = tiles
        self.pos = pos
        self.map_width = tiles.game_state.map_width
        self.map_height = tiles.game_state.map_height
        self.cell = tiles.game_state.map.get_cell(pos.x, pos.y)
        self.__is_owned_by_player = None
        self.__is_owned_by_opponent = None
        self.__is_owned = None

        self.__is_resource = None
        self.__resource_type = None
        self.__is_wood = None
        self.__is_coal = None
        self.__is_uranium = None

        self.__is_road = None
        self.__is_city = None

        self.__is_worker = None
        self.__is_cart = None

        self.__is_empty = None
        self.__adjaced_pos = None
        self.__adjacence_dir = None
        self.__adjaced_dir_unic_pos = None
        self.__adjacence_unic_pos = None

        self.player_worker_object: Union[Unit, None] = None
        self.player_cart_object: Union[Unit, None] = None
        self.opponent_worker_object: Union[Unit, None] = None
        self.opponent_cart_object: Union[Unit, None] = None


    @property
    def is_owned_by_player(self) -> bool:
        """Is owned by player
        """
        if self.__is_owned_by_player is None:
            if self.cell.pos in self.tiles.player_own_pos:
                self.__is_owned_by_player = True
                self.__is_owned = True
            else:
                self.__is_owned_by_player = False
        return self.__is_owned_by_player

    @property
    def is_owned_by_opponent(self) -> bool:
        """Is owned by opponent
        """
        if self.__is_owned_by_opponent is None:
            if self.cell.pos in self.tiles.opponent_own_pos:
                self.__is_owned_by_opponent = True
                self.__is_owned = True
            else:
                self.__is_owned_by_opponent = False
        return self.__is_owned_by_opponent

    @property
    def is_owned(self) -> bool:
        """Is owned by any
        """
        if self.__is_owned is None:
            self.__is_owned = bool(self.cell.pos in self.tiles.own_pos)
        return self.__is_owned

    @property
    def is_resource(self) -> bool:
        """Is tile resource
        """
        if self.__is_resource is None:
            self.__is_resource = bool(self.cell in self.tiles.resources)
        return self.__is_resource

    @property
    def is_wood(self) -> bool:
        """Is tile wood
        """
        if self.__is_wood is None:
            self.__is_wood = bool(self.cell in self.tiles.woods)
        return self.__is_wood

    @property
    def is_coal(self) -> bool:
        """Is tile wood
        """
        if self.__is_coal is None:
            self.__is_coal = bool(self.cell in self.tiles.coals)
        return self.__is_coal

    @property
    def is_uranium(self) -> bool:
        """Is tile wood
        """
        if self.__is_uranium is None:
            self.__is_uranium = bool(self.cell in self.tiles.uraniums)
        return self.__is_uranium

    @property
    def resource_type(self) -> str:
        """Returns type of resource
        """
        if self.__resource_type is None:
            if self.is_wood:
                self.__resource_type = cs.RESOURCE_TYPES.WOOD
            elif self.is_coal:
                self.__resource_type = cs.RESOURCE_TYPES.COAL
            elif self.is_uranium:
                self.__resource_type = cs.RESOURCE_TYPES.URANIUM
            else:
                self.__resource_type = 'notype'
        return self.__resource_type

    @property
    def is_road(self) -> bool:
        """Is tile Road
        """
        if self.__is_road is None:
            self.__is_road = bool(self.cell in self.tiles.roads)
        return self.__is_road

    @property
    def is_city(self) -> bool:
        """Is tile city
        """
        if self.__is_city is None:
            self.__is_city = bool(self.cell.citytile in self.tiles.citytiles)
        return self.__is_city

    @property
    def is_worker(self) -> bool:
        """Is tile worker
        """
        if self.__is_worker is None:
            x, y = self.cell.pos
            self.__is_worker = bool(Position(x, y) in self.tiles.workers_pos)
        return self.__is_worker

    @property
    def is_cart(self) -> bool:
        """Is tile cart
        """
        if self.__is_cart is None:
            x, y = self.cell.pos
            self.__is_worker = bool(Position(x, y) in self.tiles.carts_pos)
        return self.__is_cart

    @property
    def is_empty(self) -> bool:
        """Is tile empty
        """
        if self.__is_empty is None:
            if self.cell.pos in self.tiles.empty_pos:
                self.__is_empty = True
            else:
                self.__is_empty = False
        return self.__is_empty
    
    @property
    def adjacence_unic_pos(self) -> UnicPos:
        """Adjaced coordinates

        Returns:
            UnicPos: set of tuples
        """
        if self.__adjacence_unic_pos is None:
            self.__adjacence_unic_pos = set(AD[self.map_width]['adjacence'][(self.pos.x, self.pos.y)].keys())
        return self.__adjacence_unic_pos

    @property
    def adjacence_dir(self) -> Dict[str, Position]:
        """Calculate dict, where keys are directions, values - positions of adjaced tiles

        Returns:
            Dict[str, Position]: dict with positions and directions
        """
        if self.__adjacence_dir is None:
            self.__adjacence_dir = {
                val: Position(key[0], key[1])
                for key, val in AD[self.map_width]['adjacence'][(self.pos.x, self.pos.y)].items()
                }
            # self.__adjacence_dir = {}
            # for dir in cs.DIRECTIONS:
            #     if dir != 'c':
            #         adjaced_cell = self.pos.translate(dir, 1)
            #         if 0 <= adjaced_cell.x < self.map_width and 0 <= adjaced_cell.y < self.map_height:
            #             self.__adjacence_dir[dir] = adjaced_cell
        return self.__adjacence_dir

    @property
    def adjaced_pos(self) -> List[Position]:
        """Calculate list of position of adjaced tiles

        Returns:
            List[Position]: list of positions
        """
        if self.__adjaced_pos is None:
            self.__adjaced_pos = list(self.adjacence_dir.values())
        return self.__adjaced_pos

    @property
    def adjaced_dir_unic_pos(self) -> Dict[str, Tuple[int]]:
        """Calculate dict, where keys are directions, values - tuples of x, y positions

        Returns:
            Dict(str, Tuple[int]): dict with directions and tuples with coordinates
        """
        if self.__adjaced_dir_unic_pos is None:
            self.__adjaced_dir_unic_pos = {
                val: key
                for key, val in AD[self.map_width]['adjacence'][(self.pos.x, self.pos.y)].items()
                }
            # self.__adjaced_dir_unic_pos = {item[0]: (item[1].x, item[1].y) for item in self.adjacence_dir.items()}
        return self.__adjaced_dir_unic_pos


class TileStatesCollection:
    """Get statement matrix across all tiles
    """

    def __init__(self, game_state: Game, tiles: TilesCollection) -> None:
        self.states_map = [[None for _ in range(game_state.map.width)] for _ in range(game_state.map.height)]
        self.tiles = tiles
        self.__player_active_obj_to_state = None
        self.__opponent_active_obj_to_state = None
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

    @property
    def player_active_obj_to_state(self) -> None:
        """init all player unit objects in collection of tile states
        """
        if self.__player_active_obj_to_state is None:
            carts = self.tiles.player_carts
            workers = self.tiles.player_workers
            for worker in workers:
                tile_state = self.get_state(worker.pos)
                tile_state.player_worker_object = worker
            for cart in carts:
                tile_state = self.get_state(cart.pos)
                tile_state.player_cart_object = cart
            self.__player_active_obj_to_state = True

    @property
    def opponent_active_obj_to_state(self) -> None:
        """init all opponent unit objects in collection of tile states
        """
        if self.__opponent_active_obj_to_state is None:
            carts = self.tiles.opponent_carts
            workers = self.tiles.opponent_workers
            for worker in workers:
                tile_state = self.get_state(worker.pos)
                tile_state.opponent_worker_object = worker
            for cart in carts:
                tile_state = self.get_state(cart.pos)
                tile_state.opponent_cart_object = cart
            self.__opponent_active_obj_to_state = True


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
        self.__tiles_to_move = None
        self.__tiles_free = None

    @property
    def tiles_to_move(self) -> UnicPos:
        """All adjaced to player units tiles

        Returns:
            UnicPos: sequence of tiles positions
        """
        if self.__tiles_to_move is None:
            coord = set()
            for pos in self.tiles.player_units_pos:
                tile_state = self.states.get_state(pos=pos).adjacence_unic_pos
                coord.update(tile_state)
            self.__tiles_to_move = coord
        return self.__tiles_to_move

    @property
    def tiles_free(self) -> UnicPos:
        """Available tiles, exclude opponent cities and units

        Returns:
            UnicPos: sequence of tiles positions
        """
        if self.__tiles_free is None:
            self.__tiles_free = self.tiles_to_move.copy()
            for coord in self.tiles_to_move:
                tile_state = self.states.get_state(pos=Position(coord[0], coord[1]))
                if tile_state.is_owned_by_opponent:
                    self.__tiles_free.discard(coord)
        return self.__tiles_free


class AdjacentToResourceCollection:
    
    def __init__(
        self,
        tiles: TilesCollection,
        states: TileStatesCollection,
        ) -> None:
        self.tiles = tiles
        self.states = states
        self.adj_coord_unic: Set(Coord) = set()
        # self.__empty_adjaced_any = None
        self.__empty_adjaced_any_pos = None
        # self.__empty_adjaced_wood = None
        self.__empty_adjaced_wood_pos = None
        # self.__empty_adjaced_wood_coal = None
        self.__empty_adjaced_wood_coal_pos = None
        
    # def _set_empty_adjaced_res(self) -> None:
    #     any_ = []
    #     wood = []
    #     wood_coal = []
    #     for coord in self.adj_coord_unic:
    #         pos = Position(coord[0], coord[1])
    #         cell = self.states.tiles.game_state.map.get_cell_by_pos(pos)
    #         state = self.states.get_state(pos)
    #         if state.is_empty:
    #             any_.append(cell)
    #             if state.is_wood:
    #                 wood.append(cell)
    #             if self.tiles.player.researched_coal() and (state.is_wood or state.is_coal):
    #                 wood_coal.append(cell)
    #     self.__empty_adjaced_any = any_
    #     self.__empty_adjaced_wood = wood
    #     self.__empty_adjaced_wood_coal = wood_coal
        
    def _set_empty_adjaced_res_pos(self) -> None:
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
        self.__empty_adjaced_any_pos = any_
        self.__empty_adjaced_wood_pos = wood
        self.__empty_adjaced_wood_coal_pos = wood_coal
        
    # def _pos(self, seq: GameObjects) -> List[Position]:
    #     """Get sequence of positions

    #     Args:
    #         seq (GameObjects): sequence of objects

    #     Returns:
    #         List[Position]: list of Positions objects
    #     """
    #     return [cell.pos for cell in seq]

    # @property
    # def empty_adjaced_any(self) -> List[Cell]:
    #     if self.__empty_adjaced_any is None:
    #         self._set_empty_adjaced_res()
    #     return self.__empty_adjaced_any
    
    @property
    def empty_adjaced_any_pos(self) -> List[Position]:
        if self.__empty_adjaced_any_pos is None:
            self._set_empty_adjaced_res_pos()
        return self.__empty_adjaced_any_pos

    # @property
    # def empty_adjaced_wood(self) -> List[Cell]:
    #     if self.__empty_adjaced_wood is None:
    #         self._set_empty_adjaced_res()
    #     return self.__empty_adjaced_wood
    
    @property
    def empty_adjaced_wood_pos(self) -> List[Position]:
        if self.__empty_adjaced_wood_pos is None:
            self._set_empty_adjaced_res_pos()
        return self.__empty_adjaced_wood_pos
    
    # @property
    # def empty_adjaced_wood_coal(self) -> List[Cell]:
    #     if self.__empty_adjaced_wood_coal is None:
    #         self._set_empty_adjaced_res()
    #     return self.__empty_adjaced_wood_coal
    
    @property
    def empty_adjaced_wood_coal_pos(self) -> List[Position]:
        if self.__empty_adjaced_wood_coal_pos is None:
            self._set_empty_adjaced_res_pos()
        return self.__empty_adjaced_wood_coal_pos


class MultiCollection:
    """Collected game statements
    """
    
    def __init__(self, game_state: Game, player: Player, opponent: Player) -> None:
        self.tiles = TilesCollection(
            game_state=game_state,
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

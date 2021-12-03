from lux.game import Game
from lux.game_objects import Player
from lux.game_objects import Unit, City, CityTile
from lux.game_map import Position, Cell, GameMap
from bots.utility import CONSTANTS as cs
from bots.utility import (
    UnicPos, GameObjects, GameActiveObject, MissionsState,
    Coord, CrossGameScore, AD
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
    
class GameSpace:
    pass


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
        for cell in self.game_space.map_cells:
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
            self.__roads = [cell for cell in self.game_space.map_cells if cell.road]
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
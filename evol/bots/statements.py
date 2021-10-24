from lux.game import Game
from lux.game_objects import Player
from lux.game_objects import Unit, City, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
import os, sys
from typing import List, Union

if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


class TilesCollection:
    """Get massives of tiles"""

    def __init__(self, game_state: Game, player: Player, opponent: Player) -> None:
        self.game_state = game_state
        self.player = player
        self.opponent = opponent

        self.__map_cells = None

        self.player_units = player.units
        self.__player_units_pos = None
        self.__player_workers = None
        self.__player_workers_pos = None
        self.__player_carts = None
        self.__player_carts_pos = None
        self.__player_cities= None
        self.__player_citytiles = None
        self.__player_citytiles_pos = None
        self.__player_own = None
        self.__player_own_pos = None

        self.opponent_units = opponent.units
        self.__opponent_units_pos = None
        self.__opponent_workers = None
        self.__opponent_workers_pos = None
        self.__opponent_carts = None
        self.__opponent_carts_pos = None
        self.__opponent_cities = None
        self.__opponent_citytiles = None
        self.__opponent_citytiles_pos = None
        self.__opponent_own = None
        self.__opponent_own_pos = None

        self.__own = None
        self.__own_pos = None
        self.__empty = None
        self.__empty_pos = None

        self.__workers = None
        self.__workers_pos = None
        self.__carts = None
        self.__carts_pos = None

        self.__cities = None
        self.__citytiles = None
        self.__citytiles_pos = None

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


    @property
    def map_cells(self) -> List[Cell]:
        """
        Returns state of every cell on the game map.

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


    # player
    @property
    def player_units_pos(self) -> List[Position]:
        """
        Return positions of all Player's units.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the Unit (x: int, y: int).
        """
        if self.__player_units_pos is None:
            self.__player_units_pos = [unit.pos for unit in self.player_units]
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
        Return list of Player's workers positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the worker (x: int, y: int).
        """
        if self.__player_workers_pos is None:
            self.__player_workers_pos = [unit.pos for unit in self.player_workers]
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
        Return list of Player's carts positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinates of the cart (x: int, y: int).
        """
        if self.__player_carts_pos is None:
            self.__player_carts_pos= [unit.pos for unit in self.player_carts]
        return self.__player_carts_pos

    @property
    def player_cities(self) -> List[City]:
        """
        Return list of Player's Cities.

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
        Return list of Player's CityTiles.

        Args:
        Returns:
            List[CityTile]: game_object.CityTile object. Each CityTile object contain information:
            - cityid (srt): Unique ID for the City in form 'c_1';
            - cooldown (float): Cooldown time for current CityTile;
            - pos (Position): game_map.Position object for coordinate of the CityTile (x: int, y: int);
            - team (int): team = 0 for Player.
        """
        if self.__player_citytiles is None:
            _citytiles = []
            for city in self.player_cities:
                _citytiles = _citytiles + city.citytiles
            self.__player_citytiles = _citytiles
        return self.__player_citytiles

    @property
    def player_citytiles_pos(self) -> List[Position]:
        """
        Return list of Player's CityTiles positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the CityTile (x: int, y: int).
        """
        if self.__player_citytiles_pos is None:
            self.__player_citytiles_pos = [city.pos for city in self.player_citytiles]
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
            self.__player_own = list(set(self.player_units + self.player_citytiles))
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
            self.__player_own_pos = [cell.pos for cell in self.player_own]
        return self.__player_own_pos


    # opponent
    @property
    def opponent_units_pos(self) -> List[Position]:
        """
        Return positions of all Opponent's units.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the Unit (x: int, y: int).
        """
        if self.__opponent_units_pos is None:
             self.__opponent_units_pos = [unit.pos for unit in self.opponent_units]
        return  self.__opponent_units_pos

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
        Return list of Opponent's workers positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the worker (x: int, y: int).
        """
        if self.__opponent_workers_pos is None:
            self.__opponent_workers_pos = [unit.pos for unit in self.opponent_workers]
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
        Return list of Opponent's carts positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinates of the cart (x: int, y: int).
        """
        if self.__opponent_carts_pos is None:
            self.__opponent_carts_pos = [unit.pos for unit in self.opponent_carts]
        return self.__opponent_carts_pos

    @property
    def opponent_cities(self) -> List[City]:
        """
        Return list of Opponent's Cities.

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
        Return list of Opponent's CityTiles.

        Args:
        Returns:
            List[CityTile]: game_object.CityTile object. Each CityTile object contain information:
            - cityid (srt): Unique ID for the City in form 'c_1';
            - cooldown (float): Cooldown time for current CityTile;
            - pos (Position): game_map.Position object for coordinate of the CityTile (x: int, y: int);
            - team (int): team = 1 for Opponent.
        """
        if self.__opponent_citytiles is None:
            _citytiles = []
            for city in self.opponent_cities:
                _citytiles = _citytiles + city.citytiles
            self.__opponent_citytiles = _citytiles
        return self.__opponent_citytiles

    @property
    def opponent_citytiles_pos(self) -> List[Position]:
        """
        Return list of Opponent's CityTiles positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the CityTile (x: int, y: int).
        """
        if self.__opponent_citytiles_pos is None:
            self.__opponent_citytiles_pos = [city.pos for city in self.__opponent_citytiles]  # FIXME fixed, need check
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
            self.__opponent_own = list(set(self.opponent_units + self.opponent_citytiles))
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
            self.__opponent_own_pos = [cell.pos for cell in self.opponent_own]
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
    def empty(self) -> List[Cell]: # FIXME: gorgeous
        """
        Returns list of all empty Cell objects on game map.

        Args:
        Returns:
            List[Cell]: game_map.Cell object. Every Cell contain information about:
                - citytile (NoneType): None;
                - pos (Position): game_map.Position object for coordinate of the Cell (x: int, y: int);
                - resource (NoneType): None
                - road (int): 0.
        """
        if self.__empty is None:
            self.__empty = list(set(self.map_cells).difference(
                set(self.own), 
                set(self.roads), 
                set(self.resources)
                ))
        return self.__empty

    @property
    def empty_pos(self) -> List[Position]:
        """
        Returns list of Position of all empty Cell objects on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the empty Cell (x: int, y: int);
        """
        if self.__empty_pos is None:
            self.__empty_pos = [cell.pos for cell in self.empty]
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
        Return list of Player's and Opponent's workers positions.

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
        Returns:  # TODO type must be checked
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
        Return list of Player's and Opponent's carts positions.

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
        Return list of Player's and Opponent's Cities.

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
        Return list of Player's and Opponent's CityTiles.

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
        Return list of Player's and Opponent's CityTiles positions.

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
        Return list of Cells with road on game map.

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
        Return list of positions of tiles with road.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the tile (x: int, y: int).
        """
        if self.__roads_pos is None:
            self.__roads_pos = [cell.pos for cell in self.roads]
        return self.__roads_pos


    # resources
    @property
    def resources(self) -> List[Cell]:
        """
        Return list of Cells with resource of any type on game map.

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
            self.__resources = [cell for cell in self.map_cells if cell.has_resource()]
        return self.__resources

    @property
    def resources_pos(self) -> List[Position]:
        """
        Return list of positions of all resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the resource (x: int, y: int).
        """
        if self.__resources_pos is None:
            self.__resources_pos = [cell.pos for cell in self.resources]
        return self.__resources_pos
        
    @property
    def woods(self) -> List[Cell]:
        """
        Return list of Cells with wood resource on game map.

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
            self.__woods = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.WOOD]
        return self.__woods
    
    @property
    def woods_pos(self) -> List[Position]:
        """
        Return list of positions of wood resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the wood (x: int, y: int).
        """
        if self.__woods_pos is None:
            self.__woods_pos = [cell.pos for cell in self.woods]
        return self.__woods_pos

    @property
    def coals(self) -> List[Cell]:
        """
        Return list of Cells with coal resource on game map.

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
            self.__coals = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.COAL]
        return self.__coals
    
    @property
    def coals_pos(self) -> List[Position]:
        """
        Return list of positions of coal resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the coal (x: int, y: int).
        """
        if self.__coals_pos is None:
            self.__coals_pos = [cell.pos for cell in self.coals]
        return self.__coals_pos

    @property
    def uraniums(self) -> List[Cell]:
        """
        Return list of Cells with uranium resource on game map.

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
            self.__uraniums = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.URANIUM]
        return self.__uraniums

    @property
    def uraniums_pos(self) -> List[Position]:
        """
        Return list of positions of uranium resources on game map.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the uranium (x: int, y: int).
        """
        if self.__uraniums_pos is None:
            self.__uraniums_pos = [cell.pos for cell in self.uraniums]
        return self.__uraniums_pos


class TileState:
    """Get tile statement
    """
    def __init__(self, tiles_collection: TilesCollection, pos: Position) -> None:
        self.tiles_collection = tiles_collection
        self.cell = tiles_collection.game_state.map.get_cell(pos.x, pos.y)
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


    @property
    def is_owned_by_player(self) -> bool:
        """Is owned by player
        """
        if self.__is_owned_by_player is None:
            if self.cell in self.tiles_collection.player_own:
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
            if self.cell in self.tiles_collection.opponent_own:
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
            self.__is_owned = bool(self.cell in self.tiles_collection.own)        
        return self.__is_owned


    @property
    def is_resource(self) -> bool:
        """Is tile resource
        """
        if self.__is_resource is None:
            self.__is_resource = bool(self.cell in self.tiles_collection.resources)
        return self.__is_resource
    
    @property
    def is_wood(self) -> bool:
        """Is tile wood
        """
        if self.__is_wood is None:
            self.__is_wood = bool(self.cell in self.tiles_collection.woods)
        return self.__is_wood
    
    @property
    def is_coal(self) -> bool:
        """Is tile wood
        """
        if self.__is_coal is None:
            self.__is_coal = bool(self.cell in self.tiles_collection.coals)            
        return self.__is_coal

    @property
    def is_uranium(self) -> bool:
        """Is tile wood
        """
        if self.__is_uranium is None:
            self.__is_uranium = bool(self.cell in self.tiles_collection.uraniums)
        return self.__is_uranium

    @property
    def resource_type(self) -> str:
        """Returns type of resource
        """
        if self.__resource_type is None:
            if self.cell in self.tiles_collection.woods:
                self.__resource_type = cs.RESOURCE_TYPES.WOOD
            elif self.cell in self.tiles_collection.coals:
                self.__resource_type = cs.RESOURCE_TYPES.COAL
            elif self.cell in self.tiles_collection.uraniums:
                self.__resource_type = cs.RESOURCE_TYPES.URANIUM
            else:
                self.__resource_type = 'notype'
        return self.__resource_type

    @property
    def is_road(self) -> bool:
        """Is tile Road
        """
        if self.__is_road is None:
            self.__is_road = bool(self.cell in self.tiles_collection.roads)
        return self.__is_road

    @property
    def is_city(self) -> bool:
        """Is tile city
        """
        if self.__is_city is None:
            self.__is_city = bool(self.cell in self.tiles_collection.citytiles)
        return self.__is_city

    @property
    def is_worker(self) -> bool:
        """Is tile worker
        """
        if self.__is_worker is None:
            self.__is_worker = bool(self.cell in self.tiles_collection.workers)
        return self.__is_worker
    
    @property
    def is_cart(self) -> bool:
        """Is tile worker
        """
        if self.__is_cart is None:
            self.__is_cart = bool(self.cell in self.tiles_collection.carts)
        return self.__is_cart

    @property
    def is_empty(self) -> bool:
        """Is tile empty
        """
        if self.__is_empty is None:
            if self.cell in self.tiles_collection.empty:
                self.__is_empty = True
            else:
                self.__is_empty = False
        return self.__is_empty


class StatesCollectionsCollection:
    def __init__(self, game_state: Game, tiles_collection: TilesCollection) -> None:
        self.states_map = [[None for _ in range(game_state.map.width)] for _ in range(game_state.map.height)]
        self.tiles_collection = tiles_collection
        
    def get_state(self, pos: Position):
        if self.states_map[pos.x][pos.y] is None:
            self.states_map[pos.x][pos.y] = TileState(tiles_collection=self.tiles_collection, pos=pos)
        return self.states_map[pos.x][pos.y]

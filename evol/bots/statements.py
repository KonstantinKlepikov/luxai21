from lux.game import Game
from lux.game_objects import Player
from lux.game_objects import Unit, City, CityTile
from lux.game_map import Position, Cell
from bots.utility import CONSTANTS as cs
import os, sys
from typing import List, Union, Dict

if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


class TilesCollection:
    """Get massive of tiles"""

    def __init__(self, game_state: Game, player: Player, opponent: Player) -> None:
        self.game_state = game_state
        self.player = player
        self.opponent = opponent

        self.__map_cells = None

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
        self.__empty = None
        self.__empty_pos = None

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

        self.__empty_adjacent_any_res = None
        self.__empty_adjacent_one_any_res = None
        self.__empty_adjacent_two_any_res = None
        self.__empty_adjacent_three_any_res = None
        self.__empty_adjacent_four_any_res = None
        self.__empty_adjacent_any_res_pos = None
        self.__empty_adjacent_one_any_res_pos = None
        self.__empty_adjacent_two_any_res_pos = None
        self.__empty_adjacent_three_any_res_pos = None
        self.__empty_adjacent_four_any_res_pos = None

        self.__empty_adjacent_one_wood_res = None
        self.__empty_adjacent_two_wood_res = None
        self.__empty_adjacent_three_wood_res = None
        self.__empty_adjacent_four_wood_res = None
        self.__empty_adjacent_one_wood_res_pos = None
        self.__empty_adjacent_two_wood_res_pos = None
        self.__empty_adjacent_three_wood_res_pos = None
        self.__empty_adjacent_four_wood_res_pos = None

        self.__empty_adjacent_one_coal_res = None
        self.__empty_adjacent_two_coal_res = None
        self.__empty_adjacent_three_coal_res = None
        self.__empty_adjacent_four_coal_res = None
        self.__empty_adjacent_one_coal_res_pos = None
        self.__empty_adjacent_two_coal_res_pos = None
        self.__empty_adjacent_three_coal_res_pos = None
        self.__empty_adjacent_four_coal_res_pos = None

        self.__empty_adjacent_one_uranium_res = None
        self.__empty_adjacent_two_uranium_res = None
        self.__empty_adjacent_three_uranium_res = None
        self.__empty_adjacent_four_uranium_res = None
        self.__empty_adjacent_one_uranium_res_pos = None
        self.__empty_adjacent_two_uranium_res_pos = None
        self.__empty_adjacent_three_uranium_res_pos = None
        self.__empty_adjacent_four_uranium_res_pos = None

        self.__empty_adjacent_wood_coal_res = None
        self.__empty_adjacent_wood_coal_res_pos = None
        self.__empty_adjacent_coal_uranium_res = None
        self.__empty_adjacent_coal_uranium_res_pos = None
        self.__empty_adjacent_wood_coal_uranium_res = None
        self.__empty_adjacent_wood_coal_uranium_res_pos = None

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
        Returns positions of all Player's units.

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
        Returns list of Player's workers positions.

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
        Returns list of Player's carts positions.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinates of the cart (x: int, y: int).
        """
        if self.__player_carts_pos is None:
            self.__player_carts_pos = [unit.pos for unit in self.player_carts]
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
        Returns positions of all Opponent's units.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of the Unit (x: int, y: int).
        """
        if self.__opponent_units_pos is None:
            self.__opponent_units_pos = [unit.pos for unit in self.opponent_units]
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
        Returns list of Opponent's carts positions.

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
            self.__opponent_citytiles_pos = [city.pos for city in self.opponent_citytiles]
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
    def empty(self) -> List[Cell]:  # FIXME: gorgeous
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
            self.__roads_pos = [cell.pos for cell in self.roads]
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
            self.__resources = [cell for cell in self.map_cells if cell.has_resource()]
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
            self.__resources_pos = [cell.pos for cell in self.resources]
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
            self.__woods = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.WOOD]
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
            self.__woods_pos = [cell.pos for cell in self.woods]
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
            self.__coals = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.COAL]
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
            self.__coals_pos = [cell.pos for cell in self.coals]
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
            self.__uraniums = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.URANIUM]
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
            self.__uraniums_pos = [cell.pos for cell in self.uraniums]
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
            self.__player_cities_id = [city.cityid for city in self.player_cities]
        return self.__player_cities_id

    @property
    def opponent_cities_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Opponent's cities at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'c_1'
        """
        if self.__opponent_cities_id is None:
            self.__opponent_cities_id = [city.cityid for city in self.opponent_cities]
        return self.__opponent_cities_id

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
    def player_workers_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Player's workers at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'u_1'
        """
        if self.__player_workers_id is None:
            self.__player_workers_id = [worker.id for worker in self.player_workers]
        return self.__player_workers_id

    @property
    def opponent_workers_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Opponent's workers at a game map.

        Args:
        Returns:
            List[str]: city identifier in form 'u_1'
        """
        if self.__opponent_workers_id is None:
            self.__opponent_workers_id = [worker.id for worker in self.opponent_workers]
        return self.__opponent_workers_id

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
    def player_carts_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Player's carts at a game map.

        Args:
        Returns:
            List[str]: cart identifier in form 'u_1'
        """
        if self.__player_carts_id is None:
            self.__player_carts_id = [cart.id for cart in self.player_carts]
        return self.__player_carts_id

    @property
    def opponent_carts_id(self) -> List[str]:
        """
        Returns list of unique identifiers of Opponent's carts at a game map.

        Args:
        Returns:
            List[str]: cart identifier in form 'u_1'
        """
        if self.__opponent_carts_id is None:
            self.__opponent_carts_id = [cart.id for cart in self.opponent_carts]
        return self.__opponent_carts_id

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

    def adjacent_cells(self, cell) -> List[Position]:  # TODO check if method must be property or not
        """Calculates list of adjacent Cells

        Args:
            cell: Cell object of checked cell
        Returns:
            List[Position]: list of positions of adjacent Cells
        """
        width = self.game_state.map_width
        height = self.game_state.map_height
        adjacent_cells_pos = []
        for i in cs.DIRECTIONS:
            if i != 'c':
                adjacent_cell_pos = cell.pos.translate(i, 1)
                if 0 <= adjacent_cell_pos.x < width and 0 <= adjacent_cell_pos.y < height:
                    adjacent_cells_pos.append(adjacent_cell_pos)
        return adjacent_cells_pos

    # empty cells adjacent to resources
    @property
    def empty_adjacent_any_res(self) -> Dict[int, Dict[Cell, List[str]]]:
        """
        Collects list of all empty cells, adjacent to any resource in form [(Cell, resource type)].
        Transforms this list in dictionary of cells and types of adjacent resources in form:
                {Cell: [resource type, resource type]}
        by combining repeating Cells.
        Finally split dictionary in parts according to number of adjacent resources and returns it.

        Args:
        Returns:
            Dict[N: Dict[Cell: List[resource types]]]
        """
        if self.__empty_adjacent_any_res is None:
            self.__empty_adjacent_any_res = {1: {}, 2: {}, 3: {}, 4: {}}
            adj_to_res_cells = [(self.game_state.map.get_cell_by_pos(adj_cell_pos), cell.resource.type)
                                for cell in self.resources
                                for adj_cell_pos in self.adjacent_cells(cell)
                                if adj_cell_pos in self.empty_pos]
            adj_cells_dict = {}
            for cell, resource in adj_to_res_cells:
                adj_cells_dict.setdefault(cell, []).append(resource)

            for length in range(1, 5):
                for cell, res in adj_cells_dict.items():
                    if len(res) == length:
                        self.__empty_adjacent_any_res[length].setdefault(cell, res)

        return self.__empty_adjacent_any_res

    @property
    def empty_adjacent_one_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to one resource tiles of any type.

        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_one_any_res is None:
            self.__empty_adjacent_one_any_res = self.empty_adjacent_any_res[1]
        return self.__empty_adjacent_one_any_res

    @property
    def empty_adjacent_one_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_any_res_pos is None:
            self.__empty_adjacent_one_any_res_pos = [cell.pos for cell in self.empty_adjacent_one_any_res]
        return self.__empty_adjacent_one_any_res_pos

    @property
    def empty_adjacent_two_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to two resource tiles of any type.

        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_two_any_res is None:
            self.__empty_adjacent_two_any_res = self.empty_adjacent_any_res[2]
        return self.__empty_adjacent_two_any_res

    @property
    def empty_adjacent_two_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_any_res_pos is None:
            self.__empty_adjacent_two_any_res_pos = [cell.pos for cell in self.empty_adjacent_two_any_res]
        return self.__empty_adjacent_two_any_res_pos

    @property
    def empty_adjacent_three_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to three resource tiles of any type.
        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_three_any_res is None:
            self.__empty_adjacent_three_any_res = self.empty_adjacent_any_res[3]
        return self.__empty_adjacent_three_any_res

    @property
    def empty_adjacent_three_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_any_res_pos is None:
            self.__empty_adjacent_three_any_res_pos = [cell.pos for cell in self.empty_adjacent_three_any_res]
        return self.__empty_adjacent_three_any_res_pos

    @property
    def empty_adjacent_four_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to one resource tiles of any type.
        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_four_any_res is None:
            self.__empty_adjacent_four_any_res = self.empty_adjacent_any_res[4]
        return self.__empty_adjacent_four_any_res

    @property
    def empty_adjacent_four_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to four resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_four_any_res_pos is None:
            self.__empty_adjacent_four_any_res_pos = [cell.pos for cell in self.empty_adjacent_four_any_res]
        return self.__empty_adjacent_four_any_res_pos

    @property
    def empty_adjacent_one_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to one resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_one_wood_res is None:
            self.__empty_adjacent_one_wood_res = [cell for cell, resource in self.empty_adjacent_one_any_res.items()
                                                  if {'wood'} == set(resource)]
        return self.__empty_adjacent_one_wood_res

    @property
    def empty_adjacent_one_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_wood_res_pos is None:
            self.__empty_adjacent_one_wood_res_pos = [cell.pos for cell in self.empty_adjacent_one_wood_res]
        return self.__empty_adjacent_one_wood_res_pos

    @property
    def empty_adjacent_two_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to two resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_two_wood_res is None:
            self.__empty_adjacent_two_wood_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                  if {'wood'} == set(resource)]
        return self.__empty_adjacent_two_wood_res

    @property
    def empty_adjacent_two_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_wood_res_pos is None:
            self.__empty_adjacent_two_wood_res_pos = [cell.pos for cell in self.empty_adjacent_two_wood_res]
        return self.__empty_adjacent_two_wood_res_pos

    @property
    def empty_adjacent_three_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to three resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_three_wood_res is None:
            self.__empty_adjacent_three_wood_res = [cell for cell, resource in self.empty_adjacent_three_any_res.items()
                                                    if {'wood'} == set(resource)]
        return self.__empty_adjacent_three_wood_res

    @property
    def empty_adjacent_three_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_wood_res_pos is None:
            self.__empty_adjacent_three_wood_res_pos = [cell.pos for cell in self.empty_adjacent_three_wood_res]
        return self.__empty_adjacent_three_wood_res_pos

    @property
    def empty_adjacent_four_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to four resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_four_wood_res is None:
            self.__empty_adjacent_four_wood_res = [cell for cell, resource in self.empty_adjacent_four_any_res.items()
                                                   if {'wood'} == set(resource)]
        return self.__empty_adjacent_four_wood_res

    @property
    def empty_adjacent_four_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to four wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_four_wood_res_pos is None:
            self.__empty_adjacent_four_wood_res_pos = [cell.pos for cell in self.empty_adjacent_four_wood_res]
        return self.__empty_adjacent_four_wood_res_pos

    @property
    def empty_adjacent_one_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to one resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_one_coal_res is None:
            self.__empty_adjacent_one_coal_res = [cell for cell, resource in self.empty_adjacent_one_any_res.items()
                                                  if {'coal'} == set(resource)]
        return self.__empty_adjacent_one_coal_res

    @property
    def empty_adjacent_one_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_coal_res_pos is None:
            self.__empty_adjacent_one_coal_res_pos = [cell.pos for cell in self.empty_adjacent_one_coal_res]
        return self.__empty_adjacent_one_coal_res_pos

    @property
    def empty_adjacent_two_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to two resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_two_coal_res is None:
            self.__empty_adjacent_two_coal_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                  if {'coal'} == set(resource)]
        return self.__empty_adjacent_two_coal_res

    @property
    def empty_adjacent_two_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_coal_res_pos is None:
            self.__empty_adjacent_two_coal_res_pos = [cell.pos for cell in self.empty_adjacent_two_coal_res]
        return self.__empty_adjacent_two_coal_res_pos

    @property
    def empty_adjacent_three_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to three resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_three_coal_res is None:
            self.__empty_adjacent_three_coal_res = [cell for cell, resource in self.empty_adjacent_three_any_res.items()
                                                    if {'coal'} == set(resource)]
        return self.__empty_adjacent_three_coal_res

    @property
    def empty_adjacent_three_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_coal_res_pos is None:
            self.__empty_adjacent_three_coal_res_pos = [cell.pos for cell in self.empty_adjacent_three_coal_res]
        return self.__empty_adjacent_three_coal_res_pos

    @property
    def empty_adjacent_four_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to four resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_four_coal_res is None:
            self.__empty_adjacent_four_coal_res = [cell for cell, resource in self.empty_adjacent_four_any_res.items()
                                                   if {'coal'} == set(resource)]
        return self.__empty_adjacent_four_coal_res

    @property
    def empty_adjacent_four_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to four coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_four_coal_res_pos is None:
            self.__empty_adjacent_four_coal_res_pos = [cell.pos for cell in self.empty_adjacent_four_coal_res]
        return self.__empty_adjacent_four_coal_res_pos

    @property
    def empty_adjacent_one_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to one resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_one_uranium_res is None:
            self.__empty_adjacent_one_uranium_res = [cell for cell, resource in self.empty_adjacent_one_any_res.items()
                                                     if {'uranium'} == set(resource)]
        return self.__empty_adjacent_one_uranium_res

    @property
    def empty_adjacent_one_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_uranium_res_pos is None:
            self.__empty_adjacent_one_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_one_uranium_res]
        return self.__empty_adjacent_one_uranium_res_pos

    @property
    def empty_adjacent_two_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to two resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_two_uranium_res is None:
            self.__empty_adjacent_two_uranium_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                     if {'uranium'} == set(resource)]
        return self.__empty_adjacent_two_uranium_res

    @property
    def empty_adjacent_two_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_uranium_res_pos is None:
            self.__empty_adjacent_two_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_two_uranium_res]
        return self.__empty_adjacent_two_uranium_res_pos

    @property
    def empty_adjacent_three_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to three resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_three_uranium_res is None:
            self.__empty_adjacent_three_uranium_res = [cell for cell, resource in
                                                       self.empty_adjacent_three_any_res.items()
                                                       if {'uranium'} == set(resource)]
        return self.__empty_adjacent_three_uranium_res

    @property
    def empty_adjacent_three_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_uranium_res_pos is None:
            self.__empty_adjacent_three_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_three_uranium_res]
        return self.__empty_adjacent_three_uranium_res_pos

    @property
    def empty_adjacent_four_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to four resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_four_uranium_res is None:
            self.__empty_adjacent_four_uranium_res = [cell for cell, resource in
                                                      self.empty_adjacent_four_any_res.items()
                                                      if {'uranium'} == set(resource)]
        return self.__empty_adjacent_four_uranium_res

    @property
    def empty_adjacent_four_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to four uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_four_uranium_res_pos is None:
            self.__empty_adjacent_four_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_four_uranium_res]
        return self.__empty_adjacent_four_uranium_res_pos

    @property
    def empty_adjacent_wood_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to both types of resource: wood and coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_wood_coal_res is None:
            self.__empty_adjacent_wood_coal_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                   if {'wood', 'coal'} == set(resource)] + \
                                                  [cell for cell, resource in self.empty_adjacent_three_any_res.items()
                                                   if {'wood', 'coal'} == set(resource)] + \
                                                  [cell for cell, resource in self.empty_adjacent_four_any_res.items()
                                                   if {'wood', 'coal'} == set(resource)]
        return self.__empty_adjacent_wood_coal_res

    @property
    def empty_adjacent_wood_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to wood and coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_wood_coal_res_pos is None:
            self.__empty_adjacent_wood_coal_res_pos = [cell.pos for cell in self.empty_adjacent_wood_coal_res]
        return self.__empty_adjacent_wood_coal_res_pos

    @property
    def empty_adjacent_coal_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to both types of resource: coal and uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_coal_uranium_res is None:
            self.__empty_adjacent_coal_uranium_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                      if {'coal', 'uranium'} == set(resource)] + \
                                                     [cell for cell, resource in
                                                      self.empty_adjacent_three_any_res.items()
                                                      if {'coal', 'uranium'} == set(resource)] + \
                                                     [cell for cell, resource in
                                                      self.empty_adjacent_four_any_res.items()
                                                      if {'coal', 'uranium'} == set(resource)]

        return self.__empty_adjacent_coal_uranium_res

    @property
    def empty_adjacent_coal_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to coal and uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_coal_uranium_res_pos is None:
            self.__empty_adjacent_coal_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_coal_uranium_res]
        return self.__empty_adjacent_coal_uranium_res_pos

    @property
    def empty_adjacent_wood_coal_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to both types of resource: coal and uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_wood_coal_uranium_res is None:
            self.__empty_adjacent_wood_coal_uranium_res = [cell for cell, resource
                                                           in self.empty_adjacent_three_any_res.items()
                                                           if {'wood', 'coal', 'uranium'} == set(resource)] + \
                                                          [cell for cell, resource in
                                                           self.empty_adjacent_four_any_res.items()
                                                           if {'wood', 'coal', 'uranium'} == set(resource)]

        return self.__empty_adjacent_wood_coal_uranium_res

    @property
    def empty_adjacent_wood_coal_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to wood, coal and uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_wood_coal_uranium_res_pos is None:
            self.__empty_adjacent_wood_coal_uranium_res_pos = [cell.pos for cell
                                                               in self.empty_adjacent_wood_coal_uranium_res]
        return self.__empty_adjacent_wood_coal_uranium_res_pos


class TileState:
    """Get tile statement
    """

    def __init__(self, tiles_collection: TilesCollection, pos: Position) -> None:
        self.tiles_collection = tiles_collection
        self.pos = pos
        self.map_width = tiles_collection.game_state.map_width
        self.map_height = tiles_collection.game_state.map_height
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
        self.__adjacent = None
        self.__is_controversial_by = None

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
            self.__is_city = bool(self.cell.citytile in self.tiles_collection.citytiles)
            logger.info(f'self.cell.citytile: {self.cell.citytile}')
            logger.info(f'self.tiles_collection.citytiles: {self.tiles_collection.citytiles}')
        return self.__is_city

    @property
    def is_worker(self) -> bool:
        """Is tile worker
        """
        if self.__is_worker is None:
            self.__is_worker = bool(self.cell.pos in self.tiles_collection.workers_pos) # FIXME: cell.pos is tuple, but in collection Position obj
        return self.__is_worker

    @property
    def is_cart(self) -> bool:
        """Is tile cart
        """
        if self.__is_cart is None:
            self.__is_cart = bool(self.cell.pos in self.tiles_collection.carts_pos) # FIXME: cell.pos is tuple, but in collection Position obj
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

    @property
    def adjacent(self) -> List[Position]:
        """Calculate list of position of adjacent tiles

        Returns:
            List[Position]: list of positions
        """
        if self.__adjacent is None:
            self.__adjacent = []
            for i in cs.DIRECTIONS:
                if i != 'c':
                    adjacent_cell = self.pos.translate(i, 1)
                    if 0 <= adjacent_cell.x < self.map_width and 0 <= adjacent_cell.y < self.map_height:
                        self.__adjacent.append(adjacent_cell)
        return self.__adjacent
    @property
    def is_controversial_by(self, unit: Unit) -> List[Unit]:
        """Is controversial by units

        Args:
            unit (Unit): unit, that placed on adjacent tile
        Returns:
            List[Unit]: list of units
        """
        if self.__is_controversial_by is None:
            self.__is_controversial_by = []
            self.__is_controversial_by.append(unit)
        elif unit not in self.__is_controversial_by:
            self.__is_controversial_by.append(unit)
        if len(self.__is_controversial_by) > 1:
            return self.__is_controversial_by
        else:
            return []


class StatesCollectionsCollection:
    """Get statement matrix across all tiles
    """

    def __init__(self, game_state: Game, tiles_collection: TilesCollection) -> None:
        self.states_map = [[None for _ in range(game_state.map.width)] for _ in range(game_state.map.height)]
        self.tiles_collection = tiles_collection

    def get_state(self, pos: Position) -> TileState:
        """Get TileState of any tile by position

        Args:
            pos (Position): position object

        Returns:
            [type]: TileState object for given position
        """
        if self.states_map[pos.x][pos.y] is None:
            self.states_map[pos.x][pos.y] = TileState(tiles_collection=self.tiles_collection, pos=pos)
        return self.states_map[pos.x][pos.y]

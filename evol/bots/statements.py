from lux.game import Game
from lux.game_objects import Player
from lux.game_map import Position
from bots.utility import CONSTANTS as cs
import os, sys


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
    def map_cells(self) -> list:
        if self.__map_cells is None:
            self.__map_cells = [cell for row in self.game_state.map.map for cell in row]
        return self.__map_cells


    # player
    @property
    def player_units_pos(self) -> list:
        if self.__player_units_pos is None:
            self.__player_units_pos = [unit.pos for unit in self.player_units]
        return self.__player_units_pos
    
    @property
    def player_workers(self) -> list:
        if self.__player_workers is None:
            self.__player_workers = [unit for unit in self.player_units if unit.is_worker()]
        return self.__player_workers

    @property
    def player_workers_pos(self) -> list:
        if self.__player_workers_pos is None:
            self.__player_workers_pos = [unit.pos for unit in self.player_workers]
        return self.__player_workers_pos

    @property
    def player_carts(self) -> list:
        if self.__player_carts is None:
            self.__player_carts = [unit for unit in self.player_units if unit.is_cart()]
        return self.__player_carts

    @property
    def player_carts_pos(self) -> list:
        if self.__player_carts_pos is None:
            self.__player_carts_pos= [unit.pos for unit in self.player_carts]
        return self.__player_carts_pos

    @property
    def player_cities(self) -> list:
        if self.__player_cities is None:
            self.__player_cities = list(self.player.cities.values())
        return self.__player_cities

    @property
    def player_citytiles(self) -> list:
        if self.__player_citytiles is None:
            _citytiles = []
            for city in self.player_cities:
                _citytiles = _citytiles + city.citytiles
            self.__player_citytiles = _citytiles
        return self.__player_citytiles

    @property
    def player_citytiles_pos(self) -> list:
        if self.__player_citytiles_pos is None:
            self.__player_citytiles_pos = [city.pos for city in self.player_citytiles]
        return self.__player_citytiles_pos

    @property
    def player_own(self) -> list:
        if self.__player_own is None:
            self.__player_own = list(set(self.player_units + self.player_citytiles))
        return self.__player_own

    @property
    def player_own_pos(self) -> list:
        if self.__player_own_pos is None:
            self.__player_own_pos = [cell.pos for cell in self.player_own]
        return self.__player_own_pos


    # opponent
    @property
    def opponent_units_pos(self) -> list:
        if self.__opponent_units_pos is None:
             self.__opponent_units_pos = [unit.pos for unit in self.opponent_units]
        return  self.__opponent_units_pos

    @property
    def opponent_workers(self) -> list:
        if self.__opponent_workers is None:
            self.__opponent_workers = [unit for unit in self.opponent_units if unit.is_worker()]
        return self.__opponent_workers

    @property
    def opponent_workers_pos(self) -> list:
        if self.__opponent_workers_pos is None:
            self.__opponent_workers_pos = [unit.pos for unit in self.opponent_workers]
        return self.__opponent_workers_pos

    @property
    def opponent_carts(self) -> list:
        if self.__opponent_carts is None:
            self.__opponent_carts = [unit for unit in self.opponent_units if unit.is_cart()]
        return self.__opponent_carts

    @property
    def opponent_carts_pos(self) -> list:
        if self.__opponent_carts_pos is None:
            self.__opponent_carts_pos = [unit.pos for unit in self.opponent_carts]
        return self.__opponent_carts_pos

    @property
    def opponent_cities(self) -> list:
        if self.__opponent_cities is None:
            self.__opponent_cities = list(self.opponent.cities.values())
        return self.__opponent_cities

    @property
    def opponent_citytiles(self) -> list:
        if self.__opponent_citytiles is None:
            _citytiles = []
            for city in self.opponent_cities:
                _citytiles = _citytiles + city.citytiles
            self.__opponent_citytiles = _citytiles
        return self.__opponent_citytiles

    @property
    def opponent_citytiles_pos(self) -> list:
        if self.__opponent_citytiles_pos is None:
            self.__opponent_citytiles_pos = [city.pos for city in self.citytiles]
        return self.__opponent_citytiles_pos

    @property
    def opponent_own(self) -> list:
        if self.__opponent_own is None:
            self.__opponent_own = list(set(self.opponent_units + self.opponent_citytiles))
        return self.__opponent_own

    @property
    def opponent_own_pos(self) -> list:
        if self.__opponent_own_pos is None:
            self.__opponent_own_pos = [cell.pos for cell in self.opponent_own]
        return self.__opponent_own_pos


    # owns
    @property
    def own(self) -> list:
        if self.__own is None:
            self.__own = self.player_own + self.opponent_own
        return self.__own

    @property
    def own_pos(self) -> list:
        if self.__own_pos is None:
            self.__own_pos = self.player_own_pos + self.opponent_own_pos
        return self.__own_pos

    @property
    def empty(self) -> list: # FIXME: gorgeous
        if self.__empty is None:
            self.__empty = list(set(self.map_cells).difference(
                set(self.own), 
                set(self.roads), 
                set(self.resources)
                ))
        return self.__empty

    @property
    def empty_pos(self) -> list:
        if self.__empty_pos is None:
            self.__empty_pos = [cell.pos for cell in self.empty]
        return self.__empty_pos


    # units
    @property
    def workers(self) -> list:
        if self.__workers is None:
            self.__workers = self.player_workers + self.opponent_workers            
        return self.__workers

    @property
    def workers_pos(self) -> list:
        if self.__workers_pos is None:
            self.__workers_pos = self.player_workers_pos + self.opponent_workers_pos
        return self.__workers_pos

    @property
    def carts(self) -> list:
        if self.__carts is None:
            self.__carts = self.player_carts + self.opponent_carts

        return self.__carts

    @property
    def carts_pos(self) -> list:
        if self.__carts_pos is None:
            self.__carts_pos = self.player_carts_pos + self.opponent_carts_pos
        return self.__carts_pos


    # city
    @property
    def cities(self) -> list:
        if self.__cities is None:
            self.__cities = self.player_cities + self.opponent_cities
        return self.__cities

    @property
    def citytiles(self) -> list:
        if self.__citytiles is None:
            self.__citytiles = self.player_citytiles + self.opponent_citytiles
        return self.__citytiles  

    @property
    def citytiles_pos(self) -> list:
        if self.__citytiles_pos is None:
            self.__citytiles_pos = self.player_citytiles_pos + self.opponent_citytiles_pos
        return self.__citytiles_pos


    # roads
    @property
    def roads(self) -> list:
        if self.__roads is None:
            self.__roads = [cell for cell in self.map_cells if cell.road]
        return self.__roads

    @property
    def roads_pos(self) -> list:
        if self.__roads_pos is None:
            self.__roads_pos = [cell.pos for cell in self.roads]
        return self.__roads_pos


    # resources
    @property
    def resources(self) -> list:
        if self.__resources is None:
            self.__resources = [cell for cell in self.map_cells if cell.has_resource()]
        return self.__resources

    @property
    def resources_pos(self) -> list:
        if self.__resources_pos is None:
            self.__resources_pos = [cell.pos for cell in self.resources]
        return self.__resources_pos
        
    @property
    def woods(self) -> list:
        if self.__woods is None:
            self.__woods = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.WOOD]
        return self.__woods
    
    @property
    def woods_pos(self) -> list:
        if self.__woods_pos is None:
            self.__woods_pos = [cell.pos for cell in self.woods]
        return self.__woods_pos

    @property
    def coals(self) -> list:
        if self.__coals is None:
            self.__coals = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.COAL]
        return self.__coals
    
    @property
    def coals_pos(self) -> list:
        if self.__coals_pos is None:
            self.__coals_pos = [cell.pos for cell in self.coals]
        return self.__coals_pos

    @property
    def uraniums(self) -> list:
        if self.__uraniums is None:
            self.__uraniums = [cell for cell in self.resources if cell.resource.type == cs.RESOURCE_TYPES.URANIUM]
        return self.__uraniums

    @property
    def uraniums_pos(self) -> list:
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

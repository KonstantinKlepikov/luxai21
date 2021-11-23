from lux.game_constants import GAME_CONSTANTS as cs
from lux.game_objects import Unit, CityTile
from lux.game_map import Cell, Position
from typing import List, Dict, NamedTuple, Union, Set, Tuple
from collections import namedtuple


def make_constants_nt(const: dict = cs, name: str = 'CONSTANTS') -> namedtuple:
    """Make constants namedtuple
    {
        'UNIT_TYPES': {'WORKER': 0, 'CART': 1},
        'RESOURCE_TYPES': {'WOOD': 'wood', 'COAL': 'coal', 'URANIUM': 'uranium'},
        'DIRECTIONS': {'NORTH': 'n', 'WEST': 'w', 'EAST': 'e', 'SOUTH': 's', 'CENTER': 'c'},
        'PARAMETERS': {
            'DAY_LENGTH': 30,
            'NIGHT_LENGTH': 10,
            'MAX_DAYS': 360,
            'LIGHT_UPKEEP': {'CITY': 23, 'WORKER': 4, 'CART': 10},
            'WOOD_GROWTH_RATE': 1.025,
            'MAX_WOOD_AMOUNT': 500,
            'CITY_BUILD_COST': 100,
            'CITY_ADJACENCY_BONUS': 5,
            'RESOURCE_CAPACITY': {'WORKER': 100, 'CART': 2000},
            'WORKER_COLLECTION_RATE': {'WOOD': 20, 'COAL': 5, 'URANIUM': 2},
            'RESOURCE_TO_FUEL_RATE': {'WOOD': 1, 'COAL': 10, 'URANIUM': 40},
            'RESEARCH_REQUIREMENTS': {'COAL': 50, 'URANIUM': 200},
            'CITY_ACTION_COOLDOWN': 10,
            'UNIT_ACTION_COOLDOWN': {'CART': 3, 'WORKER': 2},
            'MAX_ROAD': 6,
            'MIN_ROAD': 0,
            'CART_ROAD_DEVELOPMENT_RATE': 0.75,
            'PILLAGE_RATE': 0.5}
    }
    """
    fields = []
    data = {}
    for key, val in const.items():
        if isinstance(val, dict):
            fields.append((key, key))
            data[key] = make_constants_nt(const=val, name=key)
        else:
            fields.append((key, type(val)))
            data[key] = val
    Nt = NamedTuple(name, fields)
    nt = Nt(**data)
            
    return nt


CONSTANTS = make_constants_nt(const=cs)

# day constants
ALL_DAYS: List[int] = [x + y for x in range(30) for y in range(0, 360, 40)]
ALL_MORNINGS: List[int] = [x for x in range(0, 360, 40) if x]
ALL_NIGHTS: List[int] = [x + y for x in range(30, 40) for y in range(0, 360, 40)]


def day_or_night_number(
    current: int,
    days: List[int] = ALL_DAYS,
    nights: List[int] = ALL_NIGHTS
    ) -> int:
    """Is night or day

    Args:
        current (int): curent turn
        days (List[int], optional): days constant. Defaults to ALL_DAYS.
        nights (List[int], optional): night constant. Defaults to ALL_NIGHTS.

    Returns:
        int: the number of day or night since begin the game
    """
    if current in days:
        n = current // 30 * 2
    elif current in nights:
        n = current // 40 * 2 + 1
    return n


# Types

# objects
ObjId = str
GameActiveObject = Union[Unit, CityTile]
GameObjects = List[Union[Cell, CityTile, Unit]]
Resources = Dict[str, List[Cell]]
Coord = Tuple[int]

# positions
UnicPos = Set[Tuple[int]]
MapData = Union[Dict[Coord, Dict[Coord, Union[str, float]]], Set[Coord]]
AdjDis = Dict[int, Dict[str, MapData]]

# missions
MissionName = str
MissionsState = Dict[ObjId, MissionName]
MissionChoosed = Tuple[Union[GameActiveObject, MissionName]]
MissionsChoosed = List[MissionChoosed]
Missions = Dict[str, Union[Unit, CityTile, List[MissionName]]]

# scoring
Rewards = List[List[int]]
CrossGameScore = Dict[str, str]

# game actions
Actions = List[str]


def get_id(map_object: GameActiveObject) -> str:
    """
    Makes ID from City.cityid or Unit.id
    Used for representation objects in logging only
    """
    return map_object.cityid if "cityid" in dir(map_object) else map_object.id

def map_adjacences_and_distancies() -> AdjDis:
    
    sizes = [12, 16, 24, 32]
    coord_state = {}
    for size in sizes:
        coords = [(x, y) for x in range(size) for y in range(size)]
        data = {'adjacence': {}, 'distance': {}, 'unic_pos': set()}
        for coord in coords:
            x = coord[0]
            y = coord[1]
            
            data['unic_pos'].add(coord)

            current = Position(x, y)
            adj = {}
            if (x - 1) >= 0:
                adj[(x - 1, y)] = 'w'
            if (y + 1) < size:
                adj[(x, y + 1)] = 's'
            if (x + 1) < size:
                adj[(x + 1, y)] = 'e'
            if (y - 1) >= 0:
                adj[(x, y - 1)] = 'n'
            data['adjacence'][coord] = adj
            
            dis = {}
            for remote in coords:
                if remote != coord:
                    dis[remote] = current.distance_to(Position(remote[0], remote[1]))
            data['distance'][coord] = dis

        coord_state[size] = data

    return coord_state

AD = map_adjacences_and_distancies()

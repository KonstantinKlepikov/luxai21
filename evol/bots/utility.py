from lux.game_constants import GAME_CONSTANTS as cs
from typing import List, Dict, NamedTuple
from collections import namedtuple


def get_times_of_days() -> Dict[str, List[int]]:
    """Get information about days and nights in game statement

    Returns:
        Dict[List[int]]: dict of lists with index numbers
    """
    
    NIGHT_SOON = 25
    NIGHT_START = 30
    NIGHT_END = 39

    days = []
    evenings = []
    nights = []

    for day in range(361):
        day_time = day % 40
        if NIGHT_SOON <= day_time < NIGHT_START:
            evenings.append(day)
        elif NIGHT_START <= day_time <= NIGHT_END:
            nights.append(day)
        else:
            days.append(day)
    return {'day_list': days, 'evening_list': evenings, 'night_list': nights}


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

from lux.game_constants import GAME_CONSTANTS as cs
from typing import List, Dict
from collections import namedtuple
import random


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


# day constants
ALL_DAYS: int = [x + y for x in range(30) for y in range(0, 360, 40)]
ALL_MORNINGS: int = [x for x in range(0, 360, 40) if x]
ALL_NIGHTS: int = [x + y for x in range(30, 40) for y in range(0, 360, 40)]


class GenConstruct:

    def __init__(self) -> None:
        self.Probability = namedtuple(
            'Probability', [
                'move_to_closest_resource',
                # 'move_to_certain_resource',         # if research allows to mine coal or radium
                'move_to_closest_citytile',
                # 'move_to_build_place',              # if cargo full and not evening or night,
                                                    # without step on citytiles TODO: priotity build of wood
                # 'move_to_closest_cart',             # if cargo full and cart is close
                'move_random',
                'transfer',
                'mine',
                'pillage',
                'build',
                'u_pass',
                'research',
                'build_cart',
                'build_worker',
                'c_pass',
            ]
        )
        self.prob_len = len(self.Probability._fields)

    def rnd(self) -> int:
        """Get random int value in range [0, 10]

        Returns:
            int: random int in range [0, 10]
        """
        return random.randint(0, 10)

    def init_genome(self) -> List[namedtuple]:
        """Initialize probability timiline for start learning

        Returns:
            List[namedtuple]: lis of probability for each turn of game
        """
        genome_init = [self.rnd() for _ in range(self.prob_len)]
        prob = self.Probability._make(genome_init)
        genome = [prob for _ in range(360)]
        return genome

    def get_genome_vector(self) -> List[int]:
        """Create random genome vector

        Returns:
            List[int]: list of random int with range [0, 10]
        """
        vector = [self.rnd() for _ in range(360*self.prob_len)]
        return vector

    def convert_genome(self, vector: List[int]) -> List[namedtuple]:
        """Convert genome list to lost of named tuples

        Args:
            vector (List[int]): genom

        Returns:
            List[namedtuple]: list of named tuples representation
        """
        genome = []
        for i in range(360):
            line_v = vector[i*self.prob_len: i*self.prob_len+self.prob_len]
            genome_line = self.Probability._make(line_v)
            genome.append(genome_line)
        return genome


def make_constants_nt(cs: dict) -> namedtuple:
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
    Nt = namedtuple('CONSTANTS', list(cs.keys()))

    def make(const: dict, nested: namedtuple):
        values = []
        for key, val in const.items():
            if isinstance(val, dict):
                Nt = namedtuple(key, list(val.keys()))
                values.append(make(const=val, nested=Nt))
            else:
                values.append(val)
    
        inst = nested._make(values)

        return inst

    nt = make(const=cs, nested=Nt)

    return nt

CONSTANTS = make_constants_nt(cs)

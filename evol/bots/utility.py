from logging import getLogger, INFO, FileHandler,  Formatter,  StreamHandler
from lux.game_constants import GAME_CONSTANTS as cs
from typing import List, Dict
from collections import namedtuple
import random


def init_logger(log_file='run.log'):
    """Game logger

    Args:
        log_file (str, optional): Path to the .log file. Defaults to 'run.log'.

    Returns:
        Logger object
    """
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    handler1 = StreamHandler()
    handler1.setFormatter(Formatter("%(message)s"))
    handler2 = FileHandler(filename=log_file, mode='w')
    handler2.setFormatter(Formatter("%(message)s"))
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    return logger


def get_times_of_days() -> Dict[str, List[int]]:
    """Get information about days and nights in game statement

    Returns:
        Dict[List[int]]: dict of lists with index numbers
    """
    
    days = list(range(0, 30))
    nights = list(range(310, 360))
    mult = [0, 80, 160, 240]
    
    for i in list(range(70, 110)):
        days.extend([num + i for num in mult])
            
    for i in list(range(30, 70)):
        nights.extend([num + i for num in mult])

    return {'day_list': days, 'night_list': nights}


class GenConstruct:
    
    def __init__(self) -> None:
        self.Probability = namedtuple(
            'Probability', [
                'move_to_closest_resource',
                'move_to_closest_citytile',
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
        vector = [self.rnd() for _ in range(360*self.prob_len)]
        return vector
    
    def convert_genome(self, vector: List[int]) -> List[namedtuple]:
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

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


def rnd():
    return random.randint(0, 10)


class Probability:
    """Probabilityes of actions nominated in range 0-10
    """
    
    def __init__(self) -> None:
        self.move_to_closest_resource: int = rnd()
        self.move_to_closest_citytile: int = rnd()
        self.move_random: int = rnd()
        self.transfer: int = rnd()
        self.mine: int = rnd()
        self.pillage: int = rnd()
        self.build: int = rnd()
        self.u_pass: int = rnd()
        self.research: int = rnd()
        self.build_cart: int = rnd()
        self.build_worker: int = rnd()
        self.c_pass: int = rnd()
    

def init_genome() -> List[Probability]:
    """Initialize probability timiline for start learning

    Returns:
        List[Probability]: lis of probability for each turn of game
    """
    timeline = []
    for _ in range(360):
        prob = Probability()
        timeline.append(prob)
    return timeline


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

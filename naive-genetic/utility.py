from logging import getLogger, INFO, FileHandler,  Formatter,  StreamHandler
from lux.game_constants import GAME_CONSTANTS as c
from typing import List, Dict
from dataclasses import dataclass
from dacite import from_dict
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
    return random.randint(0, 100)


class Probability:
    """Probabilityes of actions nominated in range 0-100
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
    

def init_probability_timeline() -> List[Probability]:
    """Initialize probability timiline for start learning

    Returns:
        List[Probability]: lis of probability for each turn of game
    """
    timeline = []
    for _ in range(360):
        prob = Probability()
        timeline.append(prob)
    return timeline


def make_constants_dclass(const: dict) -> dataclass:
    """Make constants datackases"""
    
    d_const = {}
    for key, val in const.items():
        for k, v in val.items():
            d_const[key + '_' + k] = v
    
    Dclass = dataclass(type('GAME_CONST', (), {'__annotations__': {k: type(v) for k, v in d_const.items()}}))
    d_class = from_dict(data_class=Dclass, data=d_const)

    return d_class


constants_dclass = make_constants_dclass(const=c)

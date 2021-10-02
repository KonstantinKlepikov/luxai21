from logging import getLogger, INFO, FileHandler,  Formatter,  StreamHandler
from dataclasses import dataclass
from typing import List, Dict
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


@dataclass
class Probability:
    """Гnreduced probabilityes of actions nominated in range 0-100
    """
    move: int = random.randint(0, 100)
    transfer: int = random.randint(0, 100)
    mine: int = random.randint(0, 100)
    pillage: int = random.randint(0, 100)
    build: int = random.randint(0, 100)
    u_pass: int = random.randint(0, 100)
    research: int = random.randint(0, 100)
    build_cart: int = random.randint(0, 100)
    build_worker: int = random.randint(0, 100)
    c_pass: int = random.randint(0, 100)
    

def init_probability_timeline() -> List[Probability]:
    """Initialize probability timiline for start learning

    Returns:
        List[Probability]: lis of probability for each turn of game
    """
    timeline = []
    for i in range(360):
        prob = Probability()
        timeline.append(prob)
    return timeline
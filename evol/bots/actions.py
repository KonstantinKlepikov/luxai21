from lux.game_objects import Unit, CityTile
from bots.statements import TilesCollection
from typing import List, Union, Dict
from collections import namedtuple
import random
import os, sys


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


def select_actions(
    tiles_collection: TilesCollection,
    performances: List[Dict[str, Union[Unit, CityTile, str]]],
    genome: List[namedtuple]
    ) -> List[str]:
    """Select actions for every unit and citityle

    Args:
        tiles_collection (TilesCollection): collection of game tales
        performances (List[Union[UnitPerformance, CityPerformance]]): list of possible 
            performancies for every city and unit
        genome (List[float]): action genome
        logger(Logger): logger object

    Returns:
        List[str]: actions for each object in game
    """

    selected = []
    chrome = genome[tiles_collection.game_state.turn]._asdict()
    for per in performances:
        
        posible_performancies = {}
        for key in per.keys():
            if key != 'obj':
                # use genome section for each turn
                posible_performancies[key] = chrome[key]

        if posible_performancies:
            # get list of possible performances
            p_per = [key for key in posible_performancies.keys()]
            # get list of probabilities of performances
            weights = [val[1] for val in posible_performancies.items()]
            # get reduced probabilities
            s = sum(weights)
            try:
                weights = [w / s for w in weights]
            except ZeroDivisionError:
                pass
            # get random choice 
            c = random.choices(population=p_per, weights=weights)
            # append chosen performance, associated with object of unit or city
            selected.append(per[c[0]])

    logger.info(f'Current selected: {selected}')

    return selected

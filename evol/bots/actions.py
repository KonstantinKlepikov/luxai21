from lux.game_objects import Unit, CityTile
from bots.statements import TilesCollection
from bots.performances import UnitPerformance, CityPerformance, Geometric
from bots.utility import CONSTANTS as cs
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
    performances: List[Union[UnitPerformance, CityPerformance]],
    genome: List[namedtuple]
    ) -> List[Dict[Union[Unit, CityTile], str]]:
    """Select actions for every unit and citityle

    Args:
        tiles_collection (TilesCollection): collection of game tales
        performances (List[Union[UnitPerformance, CityPerformance]]): list of possible 
            performancies for every city and unit
        genome (List[float]): action genome
        logger(Logger): logger object

    Returns:
        List[Dict[Union[Unit, CityTile], str]]: objects and selected performance
    """

    selected = []
    chrome = genome[tiles_collection.game_state.turn]._asdict()
    for per in performances:
        
        for key in per.keys():
            if key != 'obj':
                # use genome section for each turn
                per[key] = chrome[key]

        # get list of posible performancies
        p_per = [key for key in per.keys() if key != 'obj']
        # get list of probabilities of performancies
        weights = [val[1] for val in per.items() if val[0] != 'obj']
        # get reduced probabilities
        s = sum(weights)
        try:
            weights = [w / s for w in weights]
        except ZeroDivisionError:
            pass            
        # get random choice 
        c = random.choices(population=p_per, weights=weights)
        # append choiced performance, associated with object of unit or city
        selected.append({'obj': per['obj'], 'action': c[0]})

    logger.info(f'Current probability: {performances}')
    logger.info(f'Current selected: {selected}')

    return selected


def get_action(
    tiles_collection: TilesCollection, 
    obj_for_act: Dict[Union[Unit, CityTile], str]
    ) -> str: #FIXME: refactoring
    """Get action for single object

    Args:
        tiles_collection (TilesCollection): collection of game tales
        Dict[Union[Unit, CityTile], str]: object and his action
        logger(Logger): logger object

    Returns:
        str: selected action of object
    """

    if isinstance(obj_for_act['obj'], Unit):
        geo = Geometric(obj_for_act['obj'].pos)
        
        if obj_for_act['action'] == 'move_to_closest_resource':
            closest = geo.get_closest_pos(tiles_collection.resources)
            dir_to_closest = obj_for_act['obj'].pos.direction_to(closest)
            return obj_for_act['obj'].move(dir_to_closest)

        if obj_for_act['action'] == 'move_to_closest_citytile':
            closest = geo.get_closest_pos(tiles_collection.citytiles)
            dir_to_closest = obj_for_act['obj'].pos.direction_to(closest)
            return obj_for_act['obj'].move(dir_to_closest)

        if obj_for_act['action'] == 'move_random':
            seq = cs.DIRECTIONS
            return obj_for_act['obj'].move(random.choice(seq=seq))

        if obj_for_act['action'] == 'transfer': # TODO: ned to know resource for trasfere and dest
            return None

        if obj_for_act['action'] == 'mine':
            return None

        if obj_for_act['action'] == 'pillage':
            return obj_for_act['obj'].pillage()

        if obj_for_act['action'] == 'build':
            return obj_for_act['obj'].build_city()

        if obj_for_act['action'] == 'u_pass':
            return None

    if isinstance(obj_for_act['obj'], CityTile):
        if obj_for_act['action'] == 'research':
            return obj_for_act['obj'].research()

        if obj_for_act['action'] == 'build_cart':
            return obj_for_act['obj'].build_cart()

        if obj_for_act['action'] == 'build_worker':
            return obj_for_act['obj'].build_worker()

        if obj_for_act['action'] == 'c_pass':
            return None

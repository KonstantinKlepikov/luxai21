from statements import TilesCollection, StatesCollectionsCollection
from lux.game_objects import Unit, CityTile
from typing import List
from performances import UnitPerformance, CityPerformance, Geometric
from utility import CONSTANTS as cs
import random
from logging import Logger


def get_action(tiles_collection: TilesCollection, obj_for_act: dict) -> str: #FIXME: refactoring

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


def get_actions(
    genome: List[List[float]],
    tiles_collection: TilesCollection, 
    states_collection: StatesCollectionsCollection,
    logger: Logger,
    ) -> List[str]:
    """Get bot actions

    Args:
        genome (List[float]): action genome
        tiles_collection (TilesCollection): collection of game tales
        states_collection (StatesCollectionsCollection): collection of game tiles statements
        logger(Logger): logger object

    Returns:
        List[str]: list of game action for each players object on board
    """

    actions = []
    
    # get possible performances list that contains two dicts - for units and citytiles seperately
    performances = []

    for unit in tiles_collection.player_units:
        act = UnitPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            unit=unit)
        performances.append(act.get_actions())

    for citytile in tiles_collection.player_citytiles:
        act = CityPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            citytile=citytile)
        performances.append(act.get_actions())


    logger.info(f'Current performancies: {performances}')


    # get probabilities of units and cttytiles performancies and get reduced probability
    selected = []    
    for per in performances:
        
        for key in per.keys():
            if key != 'obj':
                # use genome section for each turn
                per[key] = genome[tiles_collection.game_state.turn].__dict__[key]

        # get list of posible performancies
        p_per = [key for key in per.keys() if key != 'obj']
        # get list of probabilities of performancies
        weights = [val[1] for val in per.items() if val[0] != 'obj']
        # get reduced probabilities
        s = sum(weights)
        if not s:
            s = 0.000000001 # prevent division by 0
        weights = [w / s for w in weights]
        # get random choice 
        c = random.choices(population=p_per, weights=weights)
        # append choiced performance, associated with object of unit or city
        selected.append({'obj': per['obj'], 'action': c[0]})


    logger.info(f'Current probability: {performances}')
    logger.info(f'Current selected: {selected}')


    # get actions for each object
    for select in selected:
        
        act = get_action(tiles_collection=tiles_collection, obj_for_act=select)
        if act:
            actions.append(act)
            logger.info(f'Act: {act}')
            
    return actions
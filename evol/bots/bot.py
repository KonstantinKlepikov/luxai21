from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.performances import UnitPerformance, CityPerformance
from bots.actions import select_actions, get_action
from typing import List
from logging import Logger
from collections import namedtuple


def get_bot_actions(
    genome: List[namedtuple],
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
            unit=unit
            )
        performances.append(act.get_actions())

    for citytile in tiles_collection.player_citytiles:
        act = CityPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            citytile=citytile
            )
        performances.append(act.get_actions())


    logger.info(f'Current performancies: {performances}')


    # get probabilities of units and cttytiles performancies and get reduced probability
    selected = select_actions(
        tiles_collection=tiles_collection,
        performances=performances,
        genome=genome,
        logger=logger
    )

    # get actions for each object
    for select in selected:
        
        act = get_action(tiles_collection=tiles_collection, obj_for_act=select, logger=logger)
        if act:
            actions.append(act)
            logger.info(f'Act: {act}')
            
    return actions
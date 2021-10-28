from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.performances import PerformAndGetActions
from bots.actions import select_actions
from typing import List
from collections import namedtuple
import os, sys


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally


def get_bot_actions(
    genome: List[namedtuple],
    tiles_collection: TilesCollection, 
    states_collection: StatesCollectionsCollection,
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
    
    for obj_ in tiles_collection.player_units + tiles_collection.player_citytiles:
        act = PerformAndGetActions(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            obj_=obj_
        )
    performances.append(act.get_actions())
    logger.info(f'Current performancies: {performances}')


    # get probabilities of units and cttytiles performancies and get reduced probability
    actions = select_actions(
        tiles_collection=tiles_collection,
        performances=performances,
        genome=genome
    )

    return actions

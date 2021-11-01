from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.missions import PerformAndGetActions
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
    missions_state: dict
    ) -> List[str]:
    """Get bot actions

    Args:
        genome (List[float]): action genome
        tiles_collection (TilesCollection): collection of game tales
        states_collection (StatesCollectionsCollection): collection of game tiles statements
        missions_state: dict with id of object and his mission

    Returns:
        List[str]: list of game action for each players object on board
    """

    actions = []

    for obj_ in tiles_collection.player_units + tiles_collection.player_citytiles:
        logger.info(f'Obj: {obj_}')
        if obj_.id in missions_state.keys():
            PerformAndGetActions(
                tiles_collection=tiles_collection,
                states_collection=states_collection,
                obj_=obj_,
                mission=missions_state[obj_.id]
            )

    # get actions forgame
    if missions_state:
        actions = select_actions_for_missions(
            tiles_collection=tiles_collection,
            missions_state=missions_state,
            genome=genome
        )
    logger.info(f'Actions: {actions}')

    return actions

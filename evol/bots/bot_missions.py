from lux.game import Game
from lux.game_objects import Player
from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.missions import PerformMissionsAndActions
from bots.actions import select_actions
from typing import List, Dict, Tuple
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
    game_state: Game,
    player: Player,
    opponent: Player,
    missions_state: Dict[str, str]
    ) -> Tuple[List[str], Dict[str, str]]:
    """Get bot actions

    Args:
        genome (List[float]): action genome
        tiles_collection (TilesCollection): collection of game tales
        states_collection (StatesCollectionsCollection): collection of game tiles statements
        missions_state: dict with id of object and his mission

    Returns:
        List[str]: list of game action for each players object on board
    """
    
    tiles_collection = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )

    states_collection = StatesCollectionsCollection(
        game_state=game_state,
        tiles_collection=tiles_collection
        )

    actions = []
    missions = []

    for obj_ in tiles_collection.player_own:
        logger.info(f'Obj: {obj_}')
        act = PerformMissionsAndActions(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            obj_=obj_,
            mission=missions_state[obj_.id],
            obj_=obj_
        )
        mission, missions_state = act.perform_missions_and_actions()
        logger.info(f'Missions: {missions}')
        if mission:
            missions.append(mission)

    # get actions for game
    actions = select_actions(
        tiles_collection=tiles_collection,
        missions=missions,
        genome=genome
    )
    logger.info(f'Actions: {actions}')

    return actions, missions_state

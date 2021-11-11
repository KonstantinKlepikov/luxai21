from lux.game import Game
from lux.game_objects import Player
from bots.statements import MultiCollection
from bots.utility import (
    MissionsState, Actions
)
from bots.botpipe import BotPipe
from typing import List, Tuple
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
    missions_state: MissionsState
    ) -> Tuple[Actions, MissionsState]:
    """Get bot actions

    Args:
        genome (List[namedtuple]): missions genome
        game_state (Game): game state object
        player (Player): player object
        opponent (Player): opponent object
        missions_state (MissionsState): ict with id of object and his mission

    Returns:
        Tuple[Actions, MissionsState]: [description]
    """
    logger.info('======Define game objects and define variables======')
    
    collection = MultiCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )
    
    pipe = BotPipe(collection=collection, missions_state=missions_state, genome=genome)
    
    logger.info('======Define missions, missions_state, check_again======')
    pipe.define_missions_missions_state_check_again()
    
    logger.info('======Choose mission for each object======')
    pipe.choose_mission_for_each_object(method='simple')
    
    logger.info('======Get action for each mission in mission_choosen======')
    pipe.get_action_for_each_mission_in_mission_choosen()
    logger.info(f'> bot: available_pos: {pipe.available_pos}')
    logger.info(f'> bot: Actions: {pipe.actions}')
    logger.info(f'> bot: missions_state: {pipe.missions_state}')
    
    return pipe.actions, pipe.missions_state

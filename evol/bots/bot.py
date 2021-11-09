from lux.game import Game
from lux.game_objects import Player, Unit
from bots.statements import (
    TilesCollection, StatesCollectionsCollection, ContestedTilesCollection, AdjacentToResourceTilesCollection
)
from bots.missions import PerformMissions, PerformActions
from bots.utility import (
    MissionState, GameActiveObjects, Missions, Actions, MissionsChoosed
)
from typing import List, Tuple
from collections import namedtuple
import os, sys, random


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
    missions_state: MissionState
    ) -> Tuple[Actions, MissionState]:
    """Get bot actions

    Args:
        genome (List[namedtuple]): missions genome
        game_state (Game): game state object
        player (Player): player object
        opponent (Player): opponent object
        missions_state (MissionState): ict with id of object and his mission

    Returns:
        Tuple[Actions, MissionState]: [description]
    """
    logger.info('======Define game objects and define variables======')
    tiles_collection = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )

    states_collections = StatesCollectionsCollection(
        game_state=game_state,
        tiles_collection=tiles_collection
        )

    contested_collection = ContestedTilesCollection(
        tiles_collection=tiles_collection,
        states_collections=states_collections
    )

    tiles_resource_collection = AdjacentToResourceTilesCollection(
        tiles_collection=tiles_collection,
        states_collection=states_collections
    )

    available_pos = contested_collection.tiles_free_by_opponent_to_move_in.copy()
    logger.info(f'> bot: available_pos: {available_pos}')

    actions: Actions = []
    missions_per_object: List[Missions] = []
    missions_choosen: MissionsChoosed = []
    player_own: List[GameActiveObjects] = tiles_collection.player_own

    logger.info('======Define missions, missions_state, check_again======')
    logger.info(f'> player_own: {player_own}')
    for obj_ in player_own:
        logger.info(f'>>>>>>Obj: {obj_}<<<<<<')
        act = PerformMissions(
            tiles_collection=tiles_collection,
            states_collections=states_collections,
            missions_state=missions_state,
            obj_=obj_
        )
        try:
            missions, missions_state, check_again = act.perform_missions()
            logger.info(f'> bot: missions: {missions}')
            logger.info(f'> bot: Missions_state: {missions_state}')
            logger.info(f'> bot: Check again: {check_again}')
            missions_per_object.append(missions)
            if check_again:
                player_own.append(check_again)
                logger.info(f'player_own: {player_own}')
        except TypeError:
            logger.info(f'No on can make mission')

    logger.info('======Get missions per each mission in missions_per_object======')
    logger.info(f'> bot: missions_per_object: {missions_per_object}')

    if missions_per_object:
        chrome = genome[tiles_collection.game_state.turn]._asdict()

        for miss in missions_per_object:
            logger.info('------choose mission for single object------')
        
            posible_missions = {}
            for key in miss['missions']:
                logger.info(f'> bot: Key in miss["missions"]: {key}')
                # use genome section for each turn
                posible_missions[key] = chrome[key]
                logger.info(f'> bot: posible_missions: {posible_missions}')

            if posible_missions:
                # get list of possible missions
                p_miss = [key for key in posible_missions.keys()]
                # get list of probabilities of performances
                weights = [val[1] for val in posible_missions.items()]
                # get reduced probabilities
                s = sum(weights)
                try:
                    weights = [w / s for w in weights]
                except ZeroDivisionError:
                    pass
                # get random choice 
                c = random.choices(population=p_miss, weights=weights)

                # append chosen mission, associated with object of unit or city
                # If nothing to do (for example for mine) - it is skiped
                if c[0] in miss['missions']:
                    missions_choosen.append([miss['obj'], c[0]])
                    logger.info(f'> bot: mission choosed append: {missions_choosen}')
                    # add mission_state of unit to transfer statement
                    # in next turn of game
                    if isinstance(miss['obj'], Unit):
                        missions_state[miss['obj'].id] = c[0]
                        logger.info(f'> bot: missions_state added: {missions_state}')

    logger.info('======Get action for each mission in mission_choosen======')
    logger.info(f'> bot: mission_choosen: {missions_choosen}')

    if missions_choosen:
        for miss in missions_choosen:
            act = PerformActions(
                tiles_collection=tiles_collection,
                states_collections=states_collections,
                missions_state=missions_state,
                obj_=miss[0],
                available_pos=available_pos
            )
            try:
                action = act.perform_actions(miss=miss[1])
                logger.info(f'choosed action: {action}')
                if action:
                    actions.append(action)
            except TypeError:
                logger.info(f'No can act')

    logger.info(f'> bot: available_pos: {available_pos}')
    logger.info(f'> bot: Actions: {actions}')
    logger.info(f'> bot: missions_state: {missions_state}')

    return actions, missions_state

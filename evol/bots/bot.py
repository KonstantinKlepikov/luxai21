from lux.game import Game
from lux.game_objects import Player, Unit, CityTile
from bots.statements import TilesCollection, StatesCollectionsCollection
from bots.missions import PerformMissionsAndActions
from typing import List, Dict, Tuple, Union
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

    actions: List[str] = []
    missions_per_object: List[Dict[str, Union[Unit, CityTile, str]]] = []
    player_own: List[Union[Unit, CityTile]] = tiles_collection.player_own
    logger.info(f'player_own: {player_own}')

    logger.info('======get mission_actions, missions_state, check_again======')
    for obj_ in player_own:
        logger.info(f'>>>>>>Obj: {obj_}<<<<<<')
        act = PerformMissionsAndActions(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            missions_state=missions_state,
            obj_=obj_
        )
        try:
            mission_actions, missions_state, check_again = act.perform_missions_and_actions()
            logger.info(f'mission_actions: {mission_actions}')
            logger.info(f'Missions_state: {missions_state}')
            logger.info(f'Check again: {check_again}')
            missions_per_object.append(mission_actions)
            if check_again:
                player_own.append(check_again)
                logger.info(f'player_own: {player_own}')
        except TypeError:
            logger.info(f'No can act')

    logger.info(f'Missions_per_object: {missions_per_object}')
    logger.info('======get actions======')

    if missions_per_object:
        chrome = genome[tiles_collection.game_state.turn]._asdict()

        for miss in missions_per_object:
            logger.info('choose action for single object')
        
            posible_missions = {}
            for key in miss.keys():
                if key != 'obj':
                    # use genome section for each turn
                    posible_missions[key] = chrome[key]
                    logger.info(f'posible_missions: {posible_missions}')

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
                if miss[c[0]]:
                    actions.append(miss[c[0]])
                    logger.info(f'action append miss[c[0]]: {miss[c[0]]}')
                    # add mission_state of unit to transfer statement
                    # in next turn of game
                    if isinstance(miss['obj'], Unit):
                        missions_state[miss['obj'].id] = c[0]
                        logger.info(f'missions_state[miss["obj"].id]: {c[0]}')

    logger.info(f'Actions: {actions}')
    logger.info(f'missions_state: {missions_state}')

    return actions, missions_state

from lux.game_objects import Unit
from bots.statements import MultiCollection
from bots.missions import PerformMissions, PerformActions
from bots.utility import (
    MissionsState, GameActiveObjects, Missions, Actions, MissionsChoosed
)
from collections import namedtuple
from typing import List, Tuple
import os, sys, random


if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally

class BotPipe:
    
    def __init__(
        self,
        collection: MultiCollection,
        missions_state: MissionsState,
        genome: List[namedtuple]
    ) -> None:
        self.collection = collection
        self.missions_state = missions_state
        self.genome = genome
        self.available_pos = collection.contested_collection.tiles_free_by_opponent_to_move_in.copy()
        self.player_own: List[GameActiveObjects] = collection.tiles_collection.player_own
        self.actions: Actions = []
        self.missions_per_object: List[Missions] = []
        self.missions_choosen: MissionsChoosed = []
        self.missions = None
        self.check_again = None
        
    def define_missions_missions_state_check_again(self):
        logger.info('------define_missions_missions_state_check_again------')
        logger.info(f'> define_missions_missions_state_check_again: player_own: {self.player_own}')
        for obj_ in self.player_own:
            logger.info(f'>>>>>>Obj: {obj_}<<<<<<')
            act = PerformMissions(
                tiles_collection=self.collection.tiles_collection,
                states_collections=self.collection.states_collections,
                missions_state=self.missions_state,
                obj_=obj_
            )
            try:
                self.missions, self.missions_state, self.check_again = act.perform_missions()
                logger.info(f'> define_missions_missions_state_check_again: : missions: {self.missions}')
                logger.info(f'> define_missions_missions_state_check_again: : Missions_state: {self.missions_state}')
                logger.info(f'> define_missions_missions_state_check_again: : Check again: {self.check_again}')
                self.missions_per_object.append(self.missions)
                if self.check_again:
                    self.player_own.append(self.check_again)
                    logger.info(f'define_missions_missions_state_check_again: player_own: {self.player_own}')
            except TypeError:
                logger.info(f'> define_missions_missions_state_check_again: No on can get mission')
                
    def choose_mission_for_single_object(
        self,
        miss: Missions,
        chrome: dict
        ) -> None:
        logger.info('------choose_mission_for_single_object------')

        posible_missions = {}
        for key in miss['missions']:
            logger.info(f'> choose_mission_for_single_object: Key in miss["missions"]: {key}')
            # use genome section for each turn
            posible_missions[key] = chrome[key]
            logger.info(f'> choose_mission_for_single_object: posible_missions: {posible_missions}')

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
                self.missions_choosen.append([miss['obj'], c[0]])
                logger.info(f'> choose_mission_for_single_object: mission choosed append: {self.missions_choosen}')
                # add missions_state of unit to transfer statement
                # in next turn of game
                if isinstance(miss['obj'], Unit):
                    self.missions_state[miss['obj'].id] = c[0]
                    logger.info(f'> choose_mission_for_single_object: missions_state added: {self.missions_state}')

    def choose_mission_for_single_object_with_passing(
        miss: Missions,
        chrome: dict
        ) -> None:
        logger.info('------choose_mission_for_single_object_with_passing------')
        
        # get reduced probabilities
        logger.info(f'> choose_mission_for_single_object_with_passing: chrome: {chrome}')
        weights = [val[1] for val in chrome.items()]
        s = sum(weights)
        try:
            weights = [w / s for w in weights]
            replace = zip(chrome.keys(), weights)
            for place in replace:
                chrome[place[0]] = place[1]
        except ZeroDivisionError:
            pass
        logger.info(f'> choose_mission_for_single_object_with_passing: reduced chrome: {chrome}')

        # get missions
        posible_missions = {}
        for key in miss['missions']:
            logger.info(f'> choose_mission_for_single_object_with_passing: Key in miss["missions"]: {key}')
            # use genome section for each turn
            posible_missions[key] = chrome[key]
            logger.info(f'> choose_mission_for_single_object_with_passing: posible_missions: {posible_missions}')

        # if posible_missions:
        #     # get list of possible missions
        #     p_miss = [key for key in posible_missions.keys()]
        #     # get list of probabilities of performances
        #     weights = [val[1] for val in posible_missions.items()]
        #     # get reduced probabilities
        #     s = sum(weights)
        #     try:
        #         weights = [w / s for w in weights]
        #     except ZeroDivisionError:
        #         pass
        #     # get random choice 
        #     c = random.choices(population=p_miss, weights=weights)

        #     # append chosen mission, associated with object of unit or city
        #     # If nothing to do (for example for mine) - it is skiped
        #     if c[0] in miss['missions']:
        #         missions_choosen.append([miss['obj'], c[0]])
        #         logger.info(f'> bot: > choose_mission_for_single_object_with_passing: mission choosed append: {missions_choosen}')
        #         # add missions_state of unit to transfer statement
        #         # in next turn of game
        #         if isinstance(miss['obj'], Unit):
        #             missions_state[miss['obj'].id] = c[0]
        #             logger.info(f'> bot: > choose_mission_for_single_object_with_passing: missions_state added: {missions_state}')

    def choose_mission_for_each_object(self, method: str = 'simple') -> None:
        logger.info('------choose_mission_for_each_object------')
        logger.info(f'> choose_mission_for_each_object: {self.missions_per_object}')
        logger.info(f'> choose_mission_for_each_object: method {method}')
        if self.missions_per_object:
            chrome = self.genome[self.collection.tiles_collection.game_state.turn]._asdict()
            for miss in self.missions_per_object:
                if method == 'simple':
                    self.choose_mission_for_single_object(miss=miss, chrome=chrome)
                if method == 'passing':
                    self.choose_mission_for_single_object_with_passing(miss=miss, chrome=chrome)

    def get_action_for_each_mission_in_mission_choosen(self) -> None:
        logger.info('------get_action_for_each_mission_in_mission_choosen------')
        logger.info(f'> get_action_for_each_mission_in_mission_choosen: {self.missions_choosen}')
        if self.missions_choosen:
            for miss in self.missions_choosen:
                act = PerformActions(
                    tiles_collection=self.collection.tiles_collection,
                    states_collections=self.collection.states_collections,
                    missions_state=self.missions_state,
                    obj_=miss[0],
                    available_pos=self.available_pos
                )
                try:
                    action = act.perform_actions(miss=miss[1])
                    logger.info(f'choosed action: {action}')
                    if action:
                        self.actions.append(action)
                except TypeError:
                    logger.info(f'No can act')

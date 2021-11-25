from bots.genutil import GenConstruct
from lux.game import Game
from lux.game_objects import CityTile, Player, Unit
from bots.statements import TurnSpace, GameSpace
from bots.missions import PerformMissions, PerformActions
from bots.utility import (
    MissionsState, Missions, Actions, MissionsChoosed,
    GameActiveObject
)
from collections import ChainMap, namedtuple
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
    """Bot pipline class
    """
    
    def __init__(self, turn_space: TurnSpace, genome: List[namedtuple]) -> None:
        self.turn_space = turn_space
        self.genome = genome
        self.available_pos = turn_space.contested.tiles_free.copy()
        self.actions: Actions = []
        self.missions_per_object: List[Missions] = []
        self.missions_choosed: MissionsChoosed = []
        self.missions: Missions = None
        self.check_again: GameActiveObject = None
        
    def update_resource_and_unit_statements(self):
        """Update resource and unit statements and set game_space between turns statements
        
        NOTE: calculate position of resources and adjacent set in turn 0
        Then in subseqwence turns calculate new positions of resource and remove 
        difference from adjacent set
        """
        logger.info('------update_resource_and_unit_statements------')
        # init all unit objects in turn_space of tile states
        self.turn_space.states.player_active_obj_to_state

        if self.turn_space.tiles.game_state.turn == 0:
            d = {}
            for cell in self.turn_space.tiles.resources:
                state = self.turn_space.states.get_state(pos=cell.pos)
                adjacent = state.adjacence_unic_pos
                d[(cell.pos.x, cell.pos.y)] = tuple(adjacent)
                self.turn_space.game_space.adj_coord_unic.update(adjacent)
            self.turn_space.game_space.adj_stack = ChainMap(d)
            logger.info(f'> update_resource_and_unit_statements: d {len(d)}')
            logger.info(f'> update_resource_and_unit_statements: adj_coord_unic {len(self.turn_space.game_space.adj_coord_unic)}')
        else:
            logger.info(f'> update_resource_and_unit_statements: adj_coord_unic {len(self.turn_space.game_space.adj_coord_unic)}')
            d = {(cell.pos.x, cell.pos.y): None for cell in self.turn_space.tiles.resources}
            logger.info(f'> update_resource_and_unit_statements: d {len(d)}')
            stack = self.turn_space.game_space.adj_stack.new_child(d)
            logger.info(f'> update_resource_and_unit_statements: stack {len(stack)}')
            diff = {
                coord
                for val in stack.values()
                if val != None
                for coord in val
                }
            logger.info(f'> update_resource_and_unit_statements: diff {len(diff)}')
            self.turn_space.game_space.adj_coord_unic = self.turn_space.game_space.adj_coord_unic - diff
            logger.info(f'> update_resource_and_unit_statements: adj_coord_unic {len(self.turn_space.game_space.adj_coord_unic)}')

    def init_missions_and_state_and_check_again(self):
        """init missions, missions_state and check_again variable
        """
        logger.info('------init_missions_and_state_and_check_again------')
        logger.info(f'> init_missions_and_state_and_check_again: player_own: {self.turn_space.tiles.player_own}')
        for obj_ in self.turn_space.tiles.player_own:
            logger.info(f'>>>>>>Obj: {obj_}<<<<<<')
            act = PerformMissions(
                turn_space=self.turn_space,
                obj_=obj_
            )
            try:
                self.missions, self.check_again = act.perform_missions()
                logger.info(f'> init_missions_and_state_and_check_again: : missions: {self.missions}')
                logger.info(f'> init_missions_and_state_and_check_again: : Missions_state: {self.turn_space.game_space.missions_state}')
                logger.info(f'> init_missions_and_state_and_check_again: : Check again: {self.check_again}')
                self.missions_per_object.append(self.missions)
                if self.check_again:
                    self.turn_space.tiles.player_own.append(self.check_again)
                    logger.info(f'init_missions_and_state_and_check_again: player_own: {self.turn_space.tiles.player_own}')
            except TypeError:
                logger.info(f'> init_missions_and_state_and_check_again: No one can get mission')
    
    def _set_mission_choosed_and_state(self, miss: Missions, p_miss: List[str], weights: List[float]) -> None:
        """set mission_choosed and missions_state

        Args:
            miss (Missions): missions object
            p_miss (List[str]): missions names
            weights (List[float]): missions probabilities
        """
        logger.info('------_set_mission_choosed_and_state------')
        # get random choice 
        c = random.choices(population=p_miss, weights=weights)
        logger.info(f'> _get_mission: choice: {c}')
        # append chosen mission, associated with object of unit or city
        # If nothing to do (for example for mine) - it is skiped
        if c[0] in miss['missions']:
            self.missions_choosed.append((miss['obj'], c[0]))
            logger.info(f'> _get_mission: mission choosed append: {self.missions_choosed}')
            # add missions_state of unit to transfer statement
            # in next turn of game
            if isinstance(miss['obj'], Unit):
                self.turn_space.game_space.missions_state[miss['obj'].id] = c[0]
                logger.info(f'> _get_mission: missions_state added: {self.turn_space.game_space.missions_state}')

    def _set_mission_for_single_object(
        self,
        miss: Missions,
        chrome: dict
        ) -> None:
        """Set for single object

        Args:
            miss (Missions): missions for choosing
            chrome (dict): genome
        """
        logger.info('------_set_mission_for_single_object------')

        possible_missions = {}
        build = False
        for key in miss['missions']:
            logger.info(f'> _set_mission_for_single_object: Key in miss["missions"]: {key}')
            # use genome section for each turn
            if (key == "mission_build_worker") or (key == "mission_build_cart"):
                logger.info(f'> _set_mission_for_single_object: mission buld worker or cart')
                if self.turn_space.tiles.cities_can_build():
                    logger.info(f'> _set_mission_for_single_object: i can build units')
                    possible_missions[key] = chrome[key]
                    build = True
            else:
                possible_missions[key] = chrome[key]
            logger.info(f'> _set_mission_for_single_object: possible_missions: {possible_missions}')
        if build:
            self.turn_space.tiles.build_units_counter += 1
            logger.info(f'> _set_mission_for_single_object: counter '
                        f'{self.turn_space.tiles.build_units_counter}')

        if possible_missions:
            # get list of possible missions
            p_miss = list(possible_missions.keys())
            # get list of probabilities of performances
            weights = list(possible_missions.values())
            # get reduced probabilities
            s = sum(weights)
            try:
                weights = [w / s for w in weights]
            except ZeroDivisionError:
                pass
            self._set_mission_choosed_and_state(miss=miss, p_miss=p_miss, weights=weights)

    def _set_mission_for_single_object_with_passing( # FIXME: remove or fix mission choice for cities (check can_build)
        self,
        miss: Missions,
        chrome: dict,
        gen_const: GenConstruct
        ) -> None:
        """Set mission for single object with passing probability

        Args:
            miss (Missions): missions
            chrome (dict): genome
        """
        logger.info('------_set_mission_for_single_object_with_passing------')
        
        # get reduced probabilities
        logger.info(f'> _set_mission_for_single_object_with_passing: chrome: {chrome}')
        if isinstance(miss['obj'], Unit):
            if miss['obj'].is_worker():
                spec =  gen_const.workers_per
                logger.info('> _set_mission_for_single_object_with_passing: im worker')
            if miss['obj'].is_cart():
                spec =  gen_const.carts_per
                logger.info('> _set_mission_for_single_object_with_passing: im cart')
        if isinstance(miss['obj'], CityTile):
            spec = gen_const.citytiles_per
            logger.info('> _set_mission_for_single_object_with_passing: im cititile')
        chrome = {key: val for key, val in chrome.items() if key in spec}
        prob = [val[1] for val in chrome.items()]
        logger.info(f'> _set_mission_for_single_object_with_passing: chrome after spec: {chrome}')
        logger.info(f'> _set_mission_for_single_object_with_passing: unweighted prob: {prob}')
        s = sum(prob)
        try:
            prob = [w / s for w in prob]
            replace = zip(chrome.keys(), prob)
            for place in replace:
                chrome[place[0]] = place[1]
        except ZeroDivisionError:
            pass
        logger.info(f'> _set_mission_for_single_object_with_passing: reduced chrome: {chrome}')

        # get missions
        possible_missions = {}
        for key in miss['missions']:
            logger.info(f'> _set_mission_for_single_object_with_passing: Key in miss["missions"]: {key}')
            # use genome section for each turn
            possible_missions[key] = chrome[key]
            logger.info(f'> _set_mission_for_single_object_with_passing: possible_missions: {possible_missions}')

        # get probabilities of all possible missions
        all_possible_prob = sum(possible_missions.values())
        logger.info(f'> _set_mission_for_single_object_with_passing: all_possible_prob: {all_possible_prob}')
        if 0 <= all_possible_prob < 1:
            possible_missions['pass'] = 1 - all_possible_prob
        logger.info(f'> _set_mission_for_single_object_with_passing: possible_missions: {possible_missions}')

        if possible_missions:
            # get list of possible missions
            p_miss = list(possible_missions.keys())
            # get list of probabilities of performances
            weights = list(possible_missions.values())
            self._set_mission_choosed_and_state(miss=miss, p_miss=p_miss, weights=weights)

    def set_mission_and_state_for_each_object(self, gen_const: GenConstruct, method: str = 'simple') -> None:
        """Set mission and state for each object

        Args:
            method (str, optional): used method of mission choice. Defaults to 'simple'.
        """
        logger.info('------set_mission_for_each_object------')
        logger.info(f'> set_mission_for_each_object: {self.missions_per_object}')
        logger.info(f'> set_mission_for_each_object: method {method}')
        if self.missions_per_object:
            chrome = self.genome[self.turn_space.tiles.game_state.turn]._asdict()
            for miss in self.missions_per_object:
                logger.info(f'> set_mission_for_each_object: obj {miss["obj"]}')
                if method == 'simple':
                    self._set_mission_for_single_object(miss=miss, chrome=chrome)
                if method == 'passing':
                    self._set_mission_for_single_object_with_passing(
                        miss=miss,
                        chrome=chrome,
                        gen_const=gen_const
                        )

    def set_action_for_each_mission_in_mission_choosed(self) -> None:
        """Get action for each mission on this turn
        """
        logger.info('------set_action_for_each_mission_in_mission_choosed------')
        logger.info(f'> set_action_for_each_mission_in_mission_choosed: {self.missions_choosed}')
        if self.missions_choosed:
            for miss in self.missions_choosed:
                act = PerformActions(
                    turn_space=self.turn_space,
                    obj_=miss[0],
                    available_pos=self.available_pos,
                )
                try:
                    action = act.perform_actions(miss=miss[1])
                    logger.info(f'> set_action_for_each_mission_in_mission_choosed: choosed action: {action}')
                    if action:
                        self.actions.append(action)
                except TypeError:
                    logger.info('> set_action_for_each_mission_in_mission_choosed: no can act')

def get_bot_actions(
    genome: List[namedtuple],
    game_state: Game,
    player: Player,
    opponent: Player,
    game_space: GameSpace,
    gen_const: GenConstruct = None
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
    logger.info('======set game objects and define variables======')
    
    turn_space = TurnSpace(
        game_state=game_state,
        game_space=game_space,
        player=player,
        opponent=opponent
    )
    
    pipe = BotPipe(turn_space=turn_space, genome=genome)
    
    logger.info('======Update resource and unit statements======')
    pipe.update_resource_and_unit_statements()
    
    logger.info('======Set missions, missions_state, check_again======')
    pipe.init_missions_and_state_and_check_again()
    
    logger.info('======Set mission for each object======')
    pipe.set_mission_and_state_for_each_object(gen_const=gen_const, method='simple')
    # pipe.set_mission_and_state_for_each_object(gen_const=gen_const, method='passing')
    
    logger.info('======Set action for each mission in mission_choosed======')
    pipe.set_action_for_each_mission_in_mission_choosed()

    logger.info(f'> bot: available_pos: {pipe.available_pos}')
    logger.info(f'> bot: Actions: {pipe.actions}')
    logger.info(f'> bot: missions_state: {pipe.turn_space.game_space.missions_state}')
    
    return pipe.actions

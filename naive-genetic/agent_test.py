from random import choices
from lux.game import Game
from lux import annotate
import time
from utility import init_logger, init_probability_timeline
from base_action import (
    UnitPerformance, CityPerformance, get_action
)
import random

logger = init_logger(log_file='errorlogs/run.log')
logger.info(f'Start Logging...')

game_state = None
probability_timeline = init_probability_timeline()


def agent(observation, configuration):
    start = time.time()
    
    global game_state
    global probability_timeline

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    
    ### Bot code ###
    actions = []
    
    if game_state.turn == 0:
        logger.info('Agent is running!')
        
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
        
    unit_performance = []
    city_performance = []
    
    for unit in player.units:
        act = UnitPerformance(game_state=game_state, unit=unit)
        unit_performance.append(act.get_actions())

    for city in player.cities.values():
        for sitytile in city.citytiles:
            act = CityPerformance(game_state=game_state, citytile=sitytile)
            city_performance.append(act.get_actions())

    logger.info(f'Actions on turn {game_state.turn}')
    
    
    performances = unit_performance + city_performance
    
    for per in performances:
        for key in per.keys():
            if key != 'obj':
                per[key] = probability_timeline[game_state.turn].__dict__[key]
            

    logger.info(f'Current probability: {performances}')
    

    choosed = []
    for per in performances:
        population = [key for key in per.keys() if key != 'obj']
        weights = [val[1] for val in per.items() if val[0] != 'obj']
        s = sum(weights)
        if not s:
            s = 0.000000001
        weights = [w / s for w in weights]
        c = random.choices(population=population, weights=weights)
        choosed.append({'obj': per['obj'], 'action': c[0]})
        
    logger.info(f'Current choices: {choosed}')
    
    
    for ch in choosed:
        
        act = get_action(game_state=game_state, obj_for_act=ch)
        if act:
            actions.append(act)
            logger.info(f'Act: {act}')

    
    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    
    return actions

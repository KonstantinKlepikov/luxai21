from lux.game import Game
import time
from utility import init_logger, init_probability_timeline
from base_action import (
    UnitPerformance, CityPerformance, get_action
)
from statements import TilesCollection, StatesCollectionsCollection
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

    tiles_collection = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )

    states_collection = StatesCollectionsCollection(
        game_state=game_state, 
        tiles_collection=tiles_collection
        )

    # get possible performances
    performances = []
    
    for unit in tiles_collection.player_units:
        act = UnitPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            unit=unit)
        performances.append(act.get_actions())

    for citytile in tiles_collection.player_citytiles:
        act = CityPerformance(
            tiles_collection=tiles_collection,
            states_collection=states_collection,
            citytile=citytile)
        performances.append(act.get_actions())


    logger.info(f'Actions on turn {game_state.turn}')

    
    # get probabilities of performancies
    for per in performances:
        for key in per.keys():
            if key != 'obj':
                per[key] = probability_timeline[game_state.turn].__dict__[key]
            

    logger.info(f'Current probability: {performances}')
    

    # choice performance
    choised = []
    for per in performances:
        population = [key for key in per.keys() if key != 'obj']
        weights = [val[1] for val in per.items() if val[0] != 'obj']
        s = sum(weights)
        if not s:
            s = 0.000000001 # prevent division by 0
        weights = [w / s for w in weights]
        c = random.choices(population=population, weights=weights)
        choised.append({'obj': per['obj'], 'action': c[0]})
        
    logger.info(f'Current choices: {choised}')
    
    # get actions
    for obj_for_act in choised:
        
        act = get_action(tiles_collection=tiles_collection, obj_for_act=obj_for_act)
        if act:
            actions.append(act)
            logger.info(f'Act: {act}')

    
    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    
    return actions

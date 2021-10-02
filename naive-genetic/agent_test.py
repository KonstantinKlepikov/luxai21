from lux.game import Game
from lux import annotate
import time
from utility import init_logger
from base_action import (
    UnitPerformance, CityPerformance,
)


logger = init_logger(log_file='errorlogs/run.log')
logger.info(f'Start Logging...')

game_state = None


def agent(observation, configuration):
    start = time.time()
    
    global game_state
    global storaged_map_state
    global storaged_game_state

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
        actions.append(annotate.circle(0, 0))
        
    unit_performance = []
    city_performance = []
    
    for unit in game_state.players[0].units:
        act = UnitPerformance(game_state=game_state, unit=unit)
        unit_performance.append(act.get_actions())

    for city in game_state.players[0].cities.values():
        for sitytile in city.citytiles:
            act = CityPerformance(game_state=game_state, citytile=sitytile)
            city_performance.append(act.get_actions())

    logger.info(f'Actions on turn {game_state.turn}:\nUnits: {unit_performance}\nCities: {city_performance}')
    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    
    return actions

from lux.game import Game
from lux import annotate
import time
from bots.utility import init_logger


logger = init_logger(log_file='errorlogs/run.log')
logger.info(f'Start Logging...')

game_state = None


def agent(observation, configuration):
    start = time.time()
    
    global game_state

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
        
    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    
    return actions


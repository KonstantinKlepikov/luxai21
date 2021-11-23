from lux.game import Game
from bots.genutil import GenConstruct
from bots.utility import AD
import bots.bot as bot
from bots.statements import TransitionStates
from loguru import logger
import time


logger.info('Start Logging agent_random.py...')

gen_const = GenConstruct()
# genome = gen_const.init_day_genome()
genome = gen_const.init_daily_genome()
game_state = None
transited = TransitionStates()


def agent(observation, configuration):
    start = time.time()

    global game_state
    global genome
    global missions_state

    # Do not edit
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    # Bot code
    if game_state.turn == 0:
        logger.info('Agent is running!')
        # drop missions_state each game
        transited.missions_state = {}

    logger.info(f'-------------------> Start random turn {game_state.turn} <')
    logger.info(f'missions_state: {transited.missions_state}')
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    actions = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        transited=transited,
        gen_const=gen_const
        )

    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    logger.info(f'-------------------> End random turn {game_state.turn} <')

    return actions

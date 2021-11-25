from lux.game import Game
from bots.genutil import GenConstruct
import bots.bot as bot
from bots.statements import GameSpace
from loguru import logger
import datetime


logger.info('Start Logging agent_random.py...')

gen_const = GenConstruct()
# genome = gen_const.init_day_genome()
genome = gen_const.init_daily_genome()
game_state = None
game_space = GameSpace()


def agent(observation, configuration):
    start = datetime.datetime.now()

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
        # set game state of turn 0
        game_space.set_map_cells(map=game_state.map)
        game_space.set_map_positions(size=game_state.map_height)
        # drop missions_state each game
        game_space.missions_state = {}
    else:
        game_space.set_map_cells(map=game_state.map)

    logger.info(f'-------------------> Start random turn {game_state.turn} <')
    logger.info(f'missions_state: {game_space.missions_state}')
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    actions = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        game_space=game_space,
        gen_const=gen_const
        )

    end = datetime.datetime.now()
    logger.info('time on this step: {}'.format(end - start))
    logger.info(f'-------------------> End random turn {game_state.turn} <')

    return actions

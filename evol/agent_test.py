from lux.game import Game
from bots.genutil import GenConstruct
from bots import bot
from loguru import logger
import json, time


logger.info('Start Logging agent_test.py...')


with open("bots_dump/best_bot.json", "r") as f:
    genome_list = json.load(f)
gen_const = GenConstruct()
genome = gen_const.convert_genome(vector=genome_list)
game_state = None
missions_state = {}


def agent(observation, configuration):
    start = time.time()

    global game_state
    global genome
    global missions_state

    # Do not edit #
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    # Bot code #
    if game_state.turn == 0:
        logger.info('Agent is running!')

    logger.info(f'Current turn: {game_state.turn}')
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    actions, missions_state = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        missions_state=missions_state
        )

    end = time.time()
    logger.info('time on this step: {}'.format(end - start))
    logger.info('-'*20)

    return actions

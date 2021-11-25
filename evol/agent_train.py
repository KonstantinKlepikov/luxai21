from lux.game import Game
from bots.statements import GameSpace, SubGameSpace
import bots.bot as bot
from bots.scoring import TurnScoring
from loguru import logger


logger.info('Start Logging agent_train.py...')

game_state = None
gen_const = None
genome = None
subgame_space: SubGameSpace = None
game_space = GameSpace()


def agent(observation, configuration):

    global game_state
    global genome
    global game_space
    global subgame_space

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
        # drop missions_state each game
        game_space.missions_state = {}
    game_space.set_map_statements(game_state=game_state)
    
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    actions, turn_space = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        game_space=game_space,
        gen_const=gen_const
        )

    # start scoring

    if game_state.turn == 0:
        # score additional scoring for each game
        subgame_space.game_num += 1
        subgame_space.cross_game_score[subgame_space.game_num] = 0
    
    turn_scoring = TurnScoring(
        turn=game_state.turn, 
        tiles=turn_space.tiles
        )
    
    # day plus night scoring
    # score = turn_scoring.day_plus_night_turn_scoring()
    
    # each turn scoring
    score = turn_scoring.each_turn_scoring(weighted=False)
    
    if score:
        subgame_space.cross_game_score[subgame_space.game_num] =+ score

    # end scoring

    return actions

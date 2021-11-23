from lux.game import Game
from bots.statements import TilesCollection, TransitionStates
import bots.bot as bot
from bots.scoring import TurnScoring
from bots.utility import CrossGameScore, AD
from loguru import logger


logger.info('Start Logging agent_train.py...')

game_state = None
gen_const = None
genome = None
# This parametr defines the game number in a series 
# of games with the same individual
game_num: int = -1
# dict where key is a game_num and value is a that game scour
cross_game_score: CrossGameScore = {}
transited = TransitionStates()


def agent(observation, configuration):

    global game_state
    global genome
    global cross_game_score
    global game_num
    global transited

    # Do not edit
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    # Bot code
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    
    # experimental cross_game_score scoring for fitness function
    tiles = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )
    
    if game_state.turn == 0:
        # score additional scoring for each game
        game_num += 1
        cross_game_score[game_num] = 0
        # drop missions_state each game
        transited.missions_state = {}

    turn_scoring = TurnScoring(
        turn=game_state.turn, 
        tiles=tiles
        )
    
    # day plus night scoring
    # score = turn_scoring.day_plus_night_turn_scoring()
    
    # each turn scoring
    score = turn_scoring.each_turn_scoring(weighted=False)
    
    if score:
        cross_game_score[game_num] =+ score
    # end scoring

    actions = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        transited=transited,
        gen_const=gen_const
        )

    return actions

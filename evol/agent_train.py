from lux.game import Game
from bots.statements import TilesCollection
from bots import bot
from loguru import logger
from bots.scoring import TurnScoring
from typing import Dict


logger.info('Start Logging agent_train.py...')

game_state = None
genome = None
# This parametr defines the game number in a series 
# of games with the same individual
game_eval: int = -1
# dict where key is a game_eval and value is a that game scour
intermediate: Dict[int, int] = {}
missions_state = {}


def agent(observation, configuration):

    global game_state
    global genome
    global intermediate
    global game_eval
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
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    
    # experimental intermediate scoring for fitness function
    tiles_collection = TilesCollection(
        game_state=game_state,
        player=player,
        opponent=opponent
    )
    
    if game_state.turn == 0:
        # score additional scoring for each game
        game_eval += 1
        missions_state = {}
        intermediate[game_eval] = 0
        # drop missions_state each game
        missions_state = {}

    turn_scoring = TurnScoring(
        turn=game_state.turn, 
        tiles_collection=tiles_collection
        )
    
    # day plus night scoring
    # score = turn_scoring.day_plus_night_turn_scoring()
    
    # each turn scoring
    score = turn_scoring.each_turn_scoring()
    
    if score:
        intermediate[game_eval] =+ score
    # end scoring

    actions, missions_state = bot.get_bot_actions(
        genome=genome,
        game_state=game_state,
        player=player,
        opponent=opponent,
        missions_state=missions_state
        )

    return actions

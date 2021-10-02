from kaggle_environments import make
import os
import json

PLAYER = 'agent.py'
OPPONENT = 'simple_agent'
DEBUG = False

if __name__ == "__main__":
    
    if 'PLAYER' in os.environ:
        PLAYER = os.environ['PLAYER']
        
    if 'OPPONENT' in os.environ:
        OPPONENT = os.environ['OPPONENT']
        
    if 'DEBUG' in os.environ:
        DEBUG = os.environ['DEBUG']

    env = make('lux_ai_2021', configuration={'seed': 562124210, 'loglevel': 2, 'annotations': False}, debug=DEBUG)
    steps = env.run([PLAYER, OPPONENT])

    replay = env.toJSON()
    with open("replays/replay.json", "w") as f:
        json.dump(replay, f)
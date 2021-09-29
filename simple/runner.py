from kaggle_environments import make
import os

PLAYER = 'agent.py'
OPPONENT = 'simple_agent'

if __name__ == "__main__":
    
    if 'PLAYER' in os.environ:
        PLAYER = os.environ['PLAYER']
        
    if 'OPPONENT' in os.environ:
        OPPONENT = os.environ['OPPONENT']

    env = make('lux_ai_2021', configuration={'seed': 562124210, 'loglevel': 2, 'annotations': True}, debug=True)
    steps = env.run([PLAYER, OPPONENT])

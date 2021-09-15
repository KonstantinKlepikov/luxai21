from kaggle_environments import make

if __name__ == "__main__":

    env = make('lux_ai_2021', configuration={'seed': 562124210, 'loglevel': 2, 'annotations': True}, debug=False)
    steps = env.run(['agent.py', 'simple_agent'])

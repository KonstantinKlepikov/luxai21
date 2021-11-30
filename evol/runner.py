from kaggle_environments import make
from loguru import logger
import os, json
import click


@click.command()
@click.option('--debug', is_flag=True, help='set debug mode')
@click.option('--player', default='agent_test.py', show_default=True)
@click.option('--opponent', default='simple_agent', show_default=True)
@click.option('--path', 'path_to_replay', show_default=True, default='replays/replay.json')
def run(debug, player, opponent, path_to_replay):
    
    click.echo(f'Start game with player: {player}, opponent: {opponent} with debug: {debug}')
    logger.remove()
    logger.add(open(
        'errorlogs/run_test.log', 'w'),
        level='INFO',
        format='{time:HH:mm:ss} | {level} | {message}'
        )

    logger.info(
        'Start Logging...'
        f'Is logged player: {player}, opponent: {opponent} with debug: {debug}'
        )

    env = make(
        'lux_ai_2021',
        configuration={'loglevel': 1, 'annotations': False},
        debug=debug
        )

    steps = env.run([player, opponent])

    replay = env.toJSON()

    if os.path.exists(path_to_replay):
        os.remove(path_to_replay)
    with open(path_to_replay, "w") as f:
        json.dump(replay, f)


if __name__ == '__main__':
    run()

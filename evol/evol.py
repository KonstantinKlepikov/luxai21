from deap import base, creator, tools, algorithms
from kaggle_environments import evaluate
from bots.genutil import GenConstruct
from bots.scoring import FinalScoring
from bots.statements import GameSpace, SubGameSpace
import agent_train
import agent_random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from typing import List, Tuple
from loguru import logger
import os, time, datetime, json, random, multiprocessing, pickle
from dotenv import load_dotenv
import click

logger.remove()
load_dotenv(dotenv_path='shared.env')

gen_const = GenConstruct()  # get genome construction object


# Fitness calculation
def GameScoreFitness(
    individual: List[int],
    config: dict,
    num_of_episodes: int,
    agent_) -> Tuple[float]:
    """Return game statistics for evaluation criterium

    Args:
        individual (List[int]): individual genome list

    Returns:
        Tuple[float]: tuple, that contains only one value of mean rewards for first player
    """
    agent_train.gen_const = gen_const
    # agent_train.genome = gen_const.convert_day_genome(vector=individual)
    agent_train.genome = gen_const.convert_daily_genome(vector=individual)
    agent_train.subgame_space = SubGameSpace()
    agent_train.game_space = GameSpace()
    agent_random.game_space = GameSpace()
    agent_random.gen_const = gen_const
    agent_random.genome = gen_const.init_daily_genome()
    rewards = evaluate(
        'lux_ai_2021',
        [agent_train.agent, agent_],
        configuration=config,
        num_episodes=num_of_episodes,
        debug=True
        )

    # final scoring - is a scoring, calculated inside game for each game
    # plus final rewards, returned by game. SYou can see scoring strategies
    # in scoring.py
    final_scoring = FinalScoring(rewards=rewards)
    
    # day plus night final scoring
    # mean_r = final_scoring.day_plus_night_final_scoring(
    #     cross_game_score=agent_train.subgame_space.cross_game_score
    #     )
    
    # each day final scoring
    mean_r = final_scoring.each_day_final_scoring(
        cross_game_score=agent_train.subgame_space.cross_game_score
        )

    return mean_r,


# define Genetic Algorithm flow with elitism
def eaSimpleWithElitism(
    population, 
    toolbox, 
    cxpb, 
    mutpb, 
    ngen,
    stats=None,
    halloffame=None, 
    verbose=__debug__,
    freq=10
    ):
    """This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
    halloffame is used to implement an elitism mechanism. The individuals contained in the
    halloffame are directly injected into the next generation and are not subject to the
    genetic operators of selection, crossover and mutation.
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is None:
        raise ValueError("halloffame parameter must not be empty!")

    halloffame.update(population)
    hof_size = len(halloffame.items) if halloffame.items else 0

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        click.echo(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):

        # Select the next generation individuals
        offspring = toolbox.select(population, len(population) - hof_size)

        # Vary the pool of individuals
        offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # add the best back to population:
        offspring.extend(halloffame.items)

        # Update the hall of fame with the generated individuals
        halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            click.echo(logbook.stream)
        
        if gen % freq == 0:
            # Fill the dictionary using the dict(key=value[, ...]) constructor
            cp = dict(population=population, generation=gen, halloffame=halloffame,
                      logbook=logbook, rndstate=random.getstate())

            with open('bots_dump/checkpoint.pkl', "wb") as cp_file:
                pickle.dump(cp, cp_file)

    return population, logbook


@click.command()
@click.option('--seed', default=42, show_default=True, 
              type=int, help='set 0 to remove random seed')
@click.option('--size', default=0, show_default=True, type=int, 
              help='set 12, 16, 24 or 32')
@click.option('--loglevel', default=0, show_default=True, type=int, 
              help='set 0, 1, 2 or 3')
@click.option('-annotations', is_flag=True, help='on annotation mode')
@click.option('-checkpoint', is_flag=True, help='on checkpoints')
@click.option('--freq', default=10, show_default=True, 
              type=int, help='set frequincy of checkpoint')
@click.option('--episodes', 'num_of_episodes', default=10, show_default=True, 
              type=int, help='set the number of episodes for mean metrics')
@click.option('--agent', 'agent_', default='simple_agent', show_default=True, 
              type=click.Choice(['simple_agent', 'random']))
def main(seed, size, loglevel, annotations, checkpoint, freq, num_of_episodes, agent_):
    
    start = datetime.datetime.now().replace(microsecond=0)
    
    # Constants
    NUM_OF_PROCESS = multiprocessing.cpu_count()

    # Genetic Algorithm constants
    REPLICATE = int(os.environ.get('REPLICATE'))
    GENOME_LINE_LENGHT = gen_const.prob_len  # length of genome line
    GENOME_LENGHT = REPLICATE*GENOME_LINE_LENGHT  # length of genome
    TOURNAMENT_SIZE = int(os.environ.get('TOURNAMENT_SIZE'))
    POPULATION_SIZE = int(os.environ.get('POPULATION_SIZE'))
    MAX_GENERATIONS = int(os.environ.get('MAX_GENERATIONS'))
    P_CROSSOVER = float(os.environ.get('P_CROSSOVER'))
    INDPB_CROSSOVER = float(os.environ.get('INDPB_C'))/GENOME_LENGHT
    P_MUTATION = float(os.environ.get('P_MUTATION'))
    INDPB_MUTATION = float(os.environ.get('INDPB_M'))/GENOME_LENGHT
    HALL_OF_FAME_SIZE = int(os.environ.get('HALL_OF_FAME_SIZE'))

    # Game config
    config = {
        'annotations': annotations,
        'loglevel': int(loglevel)
        }
    
    if seed:
        random.seed(seed)
        config['seed'] = seed
    else:
        seed = None
        
    if size in [12, 16, 24, 32]:
        config['rows'] = size
        config['columns'] = size

    click.echo(f'Config: {config}, Opponent: {agent_}')

    if agent_ == 'random':
        agent_ = agent_random.agent
   
    # Space initialisation
    toolbox = base.Toolbox()
    # history = tools.History()

    toolbox.register('GetRnd10', random.randint, 0, 10)

    # Define a single objective, maximizing fitness strategy
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))

    # Create the Individual class based on list
    creator.create("Individual", list, fitness=creator.FitnessMax)

    # Create the individual operator to fill up an Individual instance
    toolbox.register(
        "individualCreator",
        tools.initRepeat,
        creator.Individual,
        toolbox.GetRnd10,
        GENOME_LENGHT
        )

    # Create the population operator to generate a list of individuals
    toolbox.register(
        "populationCreator",
        tools.initRepeat,
        list,
        toolbox.individualCreator
        )
    
    # Register evaluate function
    toolbox.register("evaluate", GameScoreFitness, config=config, 
                     num_of_episodes=num_of_episodes, agent_=agent_)

    # Tournament selection with tournament size
    toolbox.register("select", tools.selTournament, tournsize=TOURNAMENT_SIZE)

    # Crossover
    toolbox.register("mate", tools.cxUniform, indpb=INDPB_CROSSOVER)

    # Flip-bit mutation
    # indpb: Independent probability for each attribute to be flipped
    toolbox.register(
        "mutate",
        tools.mutUniformInt,
        low=0,
        up=10,
        indpb=INDPB_MUTATION
        )
    
    # Devine multiprocessing 
    pool = multiprocessing.Pool(processes=NUM_OF_PROCESS)
    toolbox.register("map", pool.map)

    # Use picked data
    if checkpoint:
        with open('bots_dump/checkpoint.pkl', "r") as cp_file:
            cp = pickle.load(cp_file)
        population = cp["population"]
        logbook = cp["logbook"]
        hof = cp["halloffame"]
        random.setstate(cp["rndstate"])
        click.echo('Checkpoint loaded.')
    else:
        population = toolbox.populationCreator(n=POPULATION_SIZE)
        hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # Prepare the statistics object
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    stats.register("avg", np.mean)

    # Perform the Genetic Algorithm flow with hof feature added
    population, logbook = eaSimpleWithElitism(
        population,
        toolbox,
        cxpb=P_CROSSOVER,
        mutpb=P_MUTATION,
        ngen=MAX_GENERATIONS,
        stats=stats,
        halloffame=hof,
        verbose=True,
        freq=freq
        )
    
    pool.close()
    
    timestamp = time.strftime("%m-%d_%H-%M", time.gmtime())

    # Dump best bot and hall of fame
    with open(f"bots_dump/best_bot_{timestamp}.json", "w") as f:
        json.dump(hof.items[0], f)
    with open(f"bots_dump/best_bot.json", "w") as f:
        json.dump(hof.items[0], f)
    with open(f"bots_dump/hall_of_fame_{timestamp}.json", "w") as f:
        json.dump(hof.items, f)

    # Extract statistics
    maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

    end = datetime.datetime.now().replace(microsecond=0)
    cum = end - start
    click.echo(f'Time cumulative: {cum}')

    sns.set_style("whitegrid")
    plt.figure(figsize=(8, 11), dpi=140)
    plt.plot(maxFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title(f'NUM_EPISODES: {num_of_episodes}, TOURNAMENT_SIZE: {TOURNAMENT_SIZE}\n\
POPULATION_SIZE: {POPULATION_SIZE}, MAX_GENERATIONS: {MAX_GENERATIONS}\n\
P_CROSSOVER: {P_CROSSOVER}, INDPB_CROSSOVER: {INDPB_CROSSOVER}\n\
P_MUTATION: {P_MUTATION}, INDPB_MUTATION: {INDPB_MUTATION}\n\
HALL_OF_FAME_SIZE: {HALL_OF_FAME_SIZE}, RANDOM_SEED: {seed}\n\
GENOME_LENGHT: {GENOME_LENGHT}, Time cumulative: {cum}, date: {timestamp}')
    plt.savefig(f'img/evolution_{timestamp}.png')
    click.echo(f'Visualisation complete!')


if __name__ == "__main__":
    main()

from deap import base, creator, tools, algorithms
from kaggle_environments import evaluate
from bots.utility import GenConstruct
import agent_train
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
from typing import List, Tuple
from loguru import logger
import statistics
import time
import json


logger.remove()
logger.add(open(
    'errorlogs/run_train.log', 'w'),
    level='WARNING',
    format='{time:HH:mm:ss} | {level} | {message}'
    )


# Constants
# problem constants:
gen_const = GenConstruct()
GENOME_LINE_LENGHT = gen_const.prob_len  # length of genome line
GENOME_LENGHT = 360*GENOME_LINE_LENGHT  # lenght of genome

# set the random seed:
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# game configuration
CONFIGURATIONS = {
    "rows": 12,
    "columns": 12,
    'loglevel': 0,
    'annotations': False
    }
NUM_EPISODES = 10  # number of games for mean reaward  calculating

# sise of tournament
TOURNAMENT_SIZE = 5

# Genetic Algorithm constants:
POPULATION_SIZE = 10
P_CROSSOVER = 0.9  # probability for crossover
P_MUTATION = 0.1  # probability for mutating an individual
MAX_GENERATIONS = 50  # number of steps for evolution
HALL_OF_FAME_SIZE = 5


# Space initialisation
toolbox = base.Toolbox()

toolbox.register('GetRnd10', random.randint, 0, 10)

# define a single objective, maximizing fitness strategy:
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# create the Individual class based on list:
creator.create("Individual", list, fitness=creator.FitnessMax)

# create the individual operator to fill up an Individual instance:
toolbox.register(
    "individualCreator",
    tools.initRepeat,
    creator.Individual,
    toolbox.GetRnd10,
    GENOME_LENGHT
    )

# create the population operator to generate a list of individuals:
toolbox.register(
    "populationCreator",
    tools.initRepeat,
    list,
    toolbox.individualCreator
    )


# Fitness calculation
def GameScoreFitness(individual: List[int]) -> Tuple[float]:

    agent_train.genome = gen_const.convert_genome(vector=individual)
    rewards = evaluate(
        'lux_ai_2021',
        [agent_train.agent, 'simple_agent'],
        configuration=CONFIGURATIONS,
        num_episodes=NUM_EPISODES,
        debug=False
        )
    # get first player rewards
    rewards = [l[0] for l in rewards]
    mean_r = statistics.mean(rewards)

    return mean_r,


toolbox.register("evaluate", GameScoreFitness)


# Genetic operators
# Tournament selection with tournament size
toolbox.register("select", tools.selTournament, tournsize=TOURNAMENT_SIZE)

# Single-point crossover:
toolbox.register("mate", tools.cxOnePoint)

# Flip-bit mutation:
# indpb: Independent probability for each attribute to be flipped
toolbox.register(
    "mutate",
    tools.mutUniformInt,
    low=0,
    up=10,
    indpb=1.0/GENOME_LENGHT
    )


# Genetic Algorithm flow:
def main():

    start = time.time()

    # create initial population (generation 0):
    population = toolbox.populationCreator(n=POPULATION_SIZE)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    stats.register("avg", np.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=P_CROSSOVER,
        mutpb=P_MUTATION,
        ngen=MAX_GENERATIONS,
        stats=stats,
        halloffame=hof,
        verbose=True
        )

    # Hall of Fame info and best bot:
    # print("Hall of Fame Individuals = ", *hof.items, sep="\n")
    # print("Best Ever Individual = ", hof.items[0])
    with open("bots_dump/best_bot.json", "w") as f:
        json.dump(hof.items[0], f)

    with open("bots_dump/hall_of_fame.json", "w") as f:
        json.dump(hof.items, f)

    # extract statistics:
    maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

    # plot statistics:
    sns.set_style("whitegrid")
    plt.plot(maxFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title('Max and Average Fitness over Generations')

    plt.savefig("img/evolution.png")

    end = time.time()
    print('time on this step: {}'.format(end - start))


if __name__ == "__main__":
    main()

from deap import base, creator, tools, algorithms
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
from typing import List, Tuple
from bots.utility import Probability, rnd
from collections import namedtuple
from kaggle_environments import evaluate
import statistics
import agent_train

## Constants

# problem constants:
GENOME_LINE_LENGHT = len(Probability._fields)  # length of genome line
GENOME_LENGHT = 360 # lenght of genome

# set the random seed:
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


# sise of tournament
TOURNAMENT_SIZE = 20

# set the number of episodes for get evaluate scoring
NUM_EPISODES =  20

# Genetic Algorithm constants:
POPULATION_SIZE = 20
P_CROSSOVER = 0.9  # probability for crossover
P_MUTATION = 0.1   # probability for mutating an individual
MAX_GENERATIONS = 50
HALL_OF_FAME_SIZE = 10


# set the random seed:
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


## Space initialisation

toolbox = base.Toolbox()

# create an operator that randomly returns genome line
def get_the_random_genome_line() -> List[namedtuple]:
    genome_init = [rnd() for _ in range(GENOME_LINE_LENGHT)]
    genome_line = Probability._make(genome_init)
    return genome_line

toolbox.register("RandLine", get_the_random_genome_line)

# define a single objective, maximizing fitness strategy:
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# create the Individual class based on list:
creator.create("Individual", list, fitness=creator.FitnessMax)

# create the individual operator to fill up an Individual instance:
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.RandLine, GENOME_LENGHT)

# create the population operator to generate a list of individuals:
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)


## Fitness calculation:
# compute the number of '1's in the individual
def GameScoreFitness(individual: Individual) -> Tuple[float]:
    
    agent_train.genome = individual
    rewards = evaluate(
        'lux_ai_2021', 
        [agent_train.agent, 'simple_agent'], 
        configuration={'loglevel': 0, 'annotations': False}, 
        num_episodes=NUM_EPISODES,
        debug=False
        )    
    # get first player rewards
    rewards = [l[0] for l in rewards]
    mean_r = statistics.mean(rewards)
        
    return mean_r,

toolbox.register("evaluate", GameScoreFitness)


## Genetic operators:mutFlipBit

# Tournament selection with tournament size
toolbox.register("select", tools.selTournament, tournsize=TOURNAMENT_SIZE)

# Single-point crossover:
toolbox.register("mate", tools.cxOnePoint)

# Flip-bit mutation:
# indpb: Independent probability for each attribute to be flipped
toolbox.register("mutate", tools.mutFlipBit, indpb=1.0/GENOME_LINE_LENGHT)


## Genetic Algorithm flow:
def main():

    # create initial population (generation 0):
    population = toolbox.populationCreator(n=POPULATION_SIZE)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    stats.register("avg", np.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print Hall of Fame info:
    print("Hall of Fame Individuals = ", *hof.items, sep="\n")
    print("Best Ever Individual = ", hof.items[0])

    # extract statistics:
    maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

    # plot statistics:
    sns.set_style("whitegrid")
    plt.plot(maxFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title('Max and Average Fitness over Generations')

    plt.show()


if __name__ == "__main__":
    main()
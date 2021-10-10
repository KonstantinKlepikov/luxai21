from kaggle_environments import evaluate
from bots.utility import init_genome
import statistics
import agent_train


POPULATION_RANGE = 5
NUM_EPISODES =  20

genomes = [init_genome() for _ in range(POPULATION_RANGE)]
population = {key: {'reward': None, 'genome': value} for key, value in enumerate(genomes)}


def game_sample_runner() -> float:
  
    rewards = evaluate(
        'lux_ai_2021', 
        [agent_train.agent, 'simple_agent'], 
        configuration={'loglevel': 0, 'annotations': False}, 
        num_episodes=NUM_EPISODES,
        debug=False)
    
    # get first player rewards
    rewards = [l[0] for l in rewards]
    mean_r = statistics.mean(rewards)
   
    return mean_r


if __name__ == '__main__':
    
    for k, v in population.items():
        
        agent_train.genome = v['genome']
        population[k]['reward'] = game_sample_runner()
        
    sort = list(population.items())
    sort.sort(key=lambda i: i[1]['reward'])
    for i in sort:
        print(i[1]['reward'])

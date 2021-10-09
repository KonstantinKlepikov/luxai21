from kaggle_environments import evaluate
import statistics
import agent_train
from utility import init_genome

agent_train.genome = init_genome()
NUM_EPISODES =  20


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
    
    result = game_sample_runner()
    print(result)
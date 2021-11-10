from collections import namedtuple
from typing import List
from bots.missions import (
    WorkerMission, CartMission, CityMission
)
from bots.utility import day_or_night_number
import random


class GenConstruct:

    def __init__(self) -> None:
        self.__Probability = None
        self.prob_len = len(self.Probability._fields)
    
    @property
    def Probability(self) -> namedtuple:
        """Construct the genome base from list of possible performances of objects

        Returns:
            namedtuple: empty genome object
        """
        if self.__Probability is None:
            workers_per = [method for method in dir(WorkerMission) if method.startswith('mission_')]
            carts_per = [method for method in dir(CartMission) if method.startswith('mission_')]
            citytiles_per = [method for method in dir(CityMission) if method.startswith('mission_')]
            per = list(set(workers_per + carts_per + citytiles_per))
            self.__Probability = namedtuple('Probability', per)
        return self.__Probability

    def rnd(self) -> int:
        """Get random int value in range [0, 10]

        Returns:
            int: random int in range [0, 10]
        """
        return random.randint(0, 10)

    def init_genome(self) -> List[namedtuple]:
        """Initialize probability timiline for start learning

        Returns:
            List[namedtuple]: lis of probability for each turn of game
        """
        genome_init = [self.rnd() for _ in range(self.prob_len)]
        prob = self.Probability._make(genome_init)
        genome = [prob for _ in range(360)]
        return genome

    def get_genome_vector(self) -> List[int]:
        """Create random genome vector

        Returns:
            List[int]: list of random int with range [0, 10]
        """
        vector = [self.rnd() for _ in range(360*self.prob_len)]
        return vector

    def convert_genome(self, vector: List[int]) -> List[namedtuple]:
        """Convert genome list to lost of named tuples

        Args:
            vector (List[int]): genom

        Returns:
            List[namedtuple]: list of named tuples representation
        """
        genome = []
        for i in range(360):
            line_v = vector[i * self.prob_len: i * self.prob_len + self.prob_len]
            genome_line = self.Probability._make(line_v)
            genome.append(genome_line)
        return genome

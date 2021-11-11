from collections import namedtuple
from typing import List
from bots.missions import (
    WorkerMission, CartMission, CityMission
)
import random


class GenConstruct:
    """Class where genome vector or genome tuple constructed
    """

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

    def init_day_genome(self) -> List[namedtuple]:
        """Initialize probability timiline for start learning
        for day genom model

        Returns:
            List[namedtuple]: lis of probability for each turn of game
        """
        genome = []
        for i in range(360):
            genome_init = [self.rnd() for _ in range(self.prob_len)]
            prob = self.Probability._make(genome_init)
            genome.append(prob)
        return genome
    
    def init_daily_genome(self) -> List[namedtuple]:
        """Initialize probability timiline for start learning
        for daily genom model

        Returns:
            List[namedtuple]: lis of probability for each turn of game
        """
        genome = []
        for i in range(18):
            genome_init = [self.rnd() for _ in range(self.prob_len)]
            prob = self.Probability._make(genome_init)
            if i % 2 == 0:
                gen = [prob for _ in range(30)]
            else:
                gen = [prob for _ in range(10)]
            genome= genome + gen
        return genome

    def convert_day_genome(self, vector: List[int]) -> List[namedtuple]:
        """Convert day genome list to named tuples

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
    
    def convert_daily_genome(self, vector: List[int]) -> List[namedtuple]:
        """Convert daily genome list to named tuples

        Args:
            vector (List[int]): genome

        Returns:
            List[namedtuple]: list of named tuples representation
        """
        genome = []
        for i in range(18):
            point = i * self.prob_len
            if i % 2 == 0:
                line_v = vector[point: point + self.prob_len]
                genome_line = self.Probability._make(line_v)
                gen = [genome_line for _ in range(30)]
            else:
                line_v = vector[point: point + self.prob_len]
                genome_line = self.Probability._make(line_v)
                gen = [genome_line for _ in range(10)]
            genome = genome + gen
        return genome
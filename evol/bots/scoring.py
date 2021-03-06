from bots.statements import TilesCollection
from bots.utility import ALL_MORNINGS, Rewards, CrossGameScore
import statistics


class TurnScoring:
    """Turn scorings functions for agent_train.py
    """
    
    def __init__(self, turn: int, tiles: TilesCollection) -> None:
        self.turn = turn
        self.tiles = tiles
    
    def day_plus_night_turn_scoring(self) -> int:
        """Scoring function part for usage in agent_train.py
        with day_plus_night_final_scoring()

        Returns:
            int: score
        """
        if self.turn in ALL_MORNINGS:
            score = (len(self.tiles.player_citytiles) * 10000 + \
                len(self.tiles.player_units)) \
                * self.turn / 40
            return score

    def each_turn_scoring(self, weighted: bool = True) -> int:
        """Scoring function part for usage in agent_train.py
        with each_day_final_scoring()
        
        NOTE: Each turn scoring is multipliced by turn number for weighted option.
        If turn 359 - it has additional multiplied by 10
        
        Args:
            weighted[bool]: use weight or not. Default True

        Returns:
            int: score
        """
        if weighted:
            score = (len(self.tiles.player_citytiles) * 10000 + \
                        len(self.tiles.player_units)) * self.turn
        else:
            score = len(self.tiles.player_citytiles) * 10000 + \
                        len(self.tiles.player_units)
        if self.turn == 359:
            score = score * 10
        return score


class FinalScoring:
    """Final scorings functions for evolution alghoritm
    """
    
    def __init__(self, rewards: Rewards) -> None:
        self.rewards = rewards
    
    def simple_final_scoring(self) -> int:
        """Get simple mean rewards for first player
        Returns:
            int: mean scoring
        """    
        rewards = [l[0] for l in self.rewards]
        return statistics.mean(rewards)
    
    def day_plus_night_final_scoring(self, cross_game_score: CrossGameScore) -> int:
        """Get scoring, calculated at end of each night
        and weighted closest to end of game
        
        Each morning we are scored count of player citytiles * 1000 + palyer units
        then that numper is multipliced by serial number of the morning
        for example, for 3 citytiles and 1 unit in turn 120 we have:
        (3 * 10000 + 1) * 120/40 = 93000

        Use day_plus_night_turn_scoring() from TurnScoring in agent_train.py

        Args:
            cross_game_score: dict with number of cycles as keys
            and scorinhgs as values

        Returns:
            int: mean scoring
        """
        in_rewards = list(cross_game_score.values())
        rewards = [l[0] * 9 for l in self.rewards]
        zipped_rewards = zip(in_rewards, rewards)
        sum_rewards = [x + y for (x, y) in zipped_rewards]
        return statistics.mean(sum_rewards)
    
    def each_day_final_scoring(self, cross_game_score: CrossGameScore) -> int:
        """Get scoring, calculated at end of each turn of game and
        weighted by turn number.

        Args:
            cross_game_score: dict with number of cycles as keys
            and scorinhgs as values

        Returns:
            int: mean scoring
        """
        in_rewards = list(cross_game_score.values())
        return statistics.mean(in_rewards)

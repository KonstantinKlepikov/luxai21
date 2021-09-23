from lux.game import Game
import numpy as np


class Geometry:
    
    """Game state maping in 3-dimmensional array
    
    0. resource {True: 1, False: 0}
    1. type of resource {None: 0, 'wood': 1, 'coal': 2, 'uranium': 3}
    2. resource amout
    3. road amount
    4. is cititile {True: 1, False: 0}
    5. citiid
    6. city team
    7. city cooldown
    8. can act {True: 1, False: 0}
    
    """
    
    resources = {'wood': 1, 'coal': 2, 'uranium': 3}
    teams = {0: 1, 1: 2}
    feature_lenght = 19


    def __init__(self, game_state: Game) -> None:
        
        self.game_state = game_state
        self.height = game_state.map.height
        self.width = game_state.map.width
        self.game_state_massive = np.zeros([self.height, self.width, self.feature_lenght], np.float16)


    def set_resource(self) -> None:
        
        for h in range(self.height):
            for w in range(self.width):
                
                cell = self.game_state.map.get_cell(h, w)
                cityes = {**self.game_state.players[0].cities, **self.game_state.players[1].cities}
                empty = set(range(self.feature_lenght))
                nonempty = []
                
                if cell.has_resource():
                    self.game_state_massive[h, w, 0] = 1
                    self.game_state_massive[h, w, 1] = self.resources[cell.resource.type]
                    self.game_state_massive[h, w, 2] = cell.resource.amount
                    nonempty = nonempty + [0, 1, 2,]
                    
                if cell.road:
                    self.game_state_massive[h, w, 3] = cell.road
                    nonempty = nonempty + [3,]
                    
                if cell.citytile:
                    self.game_state_massive[h, w, 4] = 1
                    self.game_state_massive[h, w, 5] = int(cell.citytile.cityid[2:])
                    self.game_state_massive[h, w, 6] = self.teams[cell.citytile.team]
                    self.game_state_massive[h, w, 7] = cell.citytile.cooldown
                    nonempty = nonempty + [4, 5, 6, 7,]
                    
                    if cell.citytile.can_act():
                        self.game_state_massive[h, w, 8] = 1
                        nonempty = nonempty + [8,]
                        
                    if cityes.get(cell.citytile.cityid, None):
                        self.game_state_massive[h, w, 9] = cityes[cell.citytile.cityid].fuel
                        self.game_state_massive[h, w, 10] = cityes[cell.citytile.cityid].get_light_upkeep()
                        nonempty = nonempty + [9, 10,]

                    
                empty = set(range(self.feature_lenght))
                for i in empty.difference(set(nonempty)):
                    self.game_state_massive[h, w, i] = 0
                    
                    
        

class UnitActions:
    pass


class CityActions:
    pass


class GameState:
    pass


if __name__ == '__main__':
    
    pass
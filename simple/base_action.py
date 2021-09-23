from lux.game import Game
import numpy as np


class Geometry:
    
    """Game state maping in 3-dimmensional array
    
    Array is orgnized as (x, y, feature vector)
    
    0. resource {True: 1, False: 0}
    1. type of resource {None: 0, 'wood': 1, 'coal': 2, 'uranium': 3}
    2. resource amout
    3. road amount
    4. is cititile {True: 1, False: 0}
    5. citiid
    6. city team
    7. city cooldown
    8. can act {True: 1, False: 0}
    9. city id
    10. city light upkeep
    11. is unit
    12. unit id
    13. unit team
    14. unit cooldown
    15. cargo wood
    16. cargo coal
    17. cargo uranium
    18. cargo space left
    19. can build
    20. can act
    
    """
    
    resources = {'wood': 1, 'coal': 2, 'uranium': 3}
    teams = {0: 1, 1: 2}
    feature_lenght = 21


    def __init__(self, game_state: Game) -> None:
        
        self.game_state = game_state
        self.height = game_state.map.height
        self.width = game_state.map.width
        self.game_state_massive = None
        self.cityes = {**self.game_state.players[0].cities, **self.game_state.players[1].cities}
        self.units = self.game_state.players[0].units + self.game_state.players[1].units

    def set_map_state(self) -> None:
        
        self.game_state_massive = np.zeros([self.height, self.width, self.feature_lenght], np.float16)
        
        for h in range(self.height):
            for w in range(self.width):
                
                cell = self.game_state.map.get_cell(w, h)
                
                if cell.has_resource():
                    self.game_state_massive[w, h, 0] = 1
                    self.game_state_massive[w, h, 1] = self.resources[cell.resource.type]
                    self.game_state_massive[w, h, 2] = cell.resource.amount
                    
                if cell.road:
                    self.game_state_massive[w, h, 3] = cell.road
                    
                if cell.citytile:
                    self.game_state_massive[w, h, 4] = 1
                    self.game_state_massive[w, h, 5] = int(cell.citytile.cityid[2:])
                    self.game_state_massive[w, h, 6] = self.teams[cell.citytile.team]
                    self.game_state_massive[w, h, 7] = cell.citytile.cooldown
                    
                    if cell.citytile.can_act():
                        self.game_state_massive[w, h, 8] = 1
                        
                    if self.cityes.get(cell.citytile.cityid, None):
                        self.game_state_massive[w, h, 9] = self.cityes[cell.citytile.cityid].fuel
                        self.game_state_massive[w, h, 10] = self.cityes[cell.citytile.cityid].get_light_upkeep()

        for unit in self.units:
            w, h = unit.pos.x, unit.pos.y
            self.game_state_massive[w, h, 11] = 1
            self.game_state_massive[w, h, 12] = int(unit.id[2:])
            self.game_state_massive[w, h, 13] = self.teams[unit.team]
            self.game_state_massive[w, h, 14] = unit.cooldown
            self.game_state_massive[w, h, 15] = unit.cargo.wood
            self.game_state_massive[w, h, 16] = unit.cargo.coal
            self.game_state_massive[w, h, 17] = unit.cargo.uranium
            self.game_state_massive[w, h, 18] = unit.get_cargo_space_left()
            self.game_state_massive[w, h, 19] = unit.can_build(self.game_state.map)
            self.game_state_massive[w, h, 20] = unit.can_act()          

class UnitActions:
    pass


class CityActions:
    pass


class GameState:
    pass


if __name__ == '__main__':
    
    pass
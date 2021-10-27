from bots.performances import Performance
from lux.game_objects import Unit
from bots.statements import TilesCollection, StatesCollectionsCollection

if __name__ == '__main__':

    cl = Performance(
        tiles_collection=TilesCollection, 
        states_collection=StatesCollectionsCollection, 
        unit=Unit)
    
    print(cl.posible_actions)
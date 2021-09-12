from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux.game_map import Cell
from lux.game_objects import Unit
from lux import annotate
import math


target_tiles = [] # to help avoid collisions


def find_resources(game_state):
    """This snippet finds all resources stored on the map and puts them into a list so we can search over them

    Args:
        game_state (obj): game_state object

    Returns:
        list: ;ist of tiles with resources
    """
    resource_tiles: list[Cell] = []
    width, height = game_state.map_width, game_state.map_height
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)

    return resource_tiles


def find_closest_resources(pos, player, resource_tiles):
    """The next snippet finds the closest resource tile that we can mine given position on a map

    Args:
        pos (obj): position object
        player (obj): player object
        resource_tiles (list): list of resource tiles objects

    Returns:
        obj: closest to position resource tile object
    """
    closest_dist = math.inf
    closest_resource_tile = None
    for resource_tile in resource_tiles:
        # we skip over resources that we can't mine due to not having researched them
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
        dist = resource_tile.pos.distance_to(pos)
        if dist < closest_dist:
            closest_dist = dist
            closest_resource_tile = resource_tile

    return closest_resource_tile


def find_nearest_position(target_position, option_positions):
    """
    target_position: Position object
    option_positions: list of Position, Cell, or Unit objects (must all be the same type)
    finds the closest option_position to the target_position
    """

    # convert option_positions list to Position objects
    if type(option_positions[0]) in [Cell, Unit]:
        option_positions = [cell.pos for cell in option_positions]
        
    # find closest position
    closest_dist = math.inf
    closest_position = None
    for position in option_positions:
        dist = target_position.distance_to(position)
        if dist < closest_dist:
            closest_dist = dist
            closest_position = position

    return closest_position


def find_closest_city_tile(pos, player):
    closest_city_tile = None
    if len(player.cities) > 0:
        closest_dist = math.inf
        # the cities are stored as a dictionary mapping city id to the city object, which has a citytiles field that
        # contains the information of all citytiles in that city
        for k, city in player.cities.items():
            for city_tile in city.citytiles:
                dist = city_tile.pos.distance_to(pos)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_city_tile = city_tile

    return closest_city_tile


def researched(resource, player):
        """
        Given a Resource object, return whether the player has researched the resource type
        """
        if resource.type == Constants.RESOURCE_TYPES.WOOD:
            return True
        if resource.type == Constants.RESOURCE_TYPES.COAL \
            and player.research_points >= GAME_CONSTANTS['PARAMETERS']['RESEARCH_REQUIREMENTS']['COAL']:
                return True
        if resource.type == Constants.RESOURCE_TYPES.URANIUM \
            and player.research_points >= GAME_CONSTANTS['PARAMETERS']['RESEARCH_REQUIREMENTS']['URANIUM']:
                return True

        return False


def get_cells(cell_type, height, width, observation, game_state, player):  # resource, researched resource, player citytile, enemy citytile, empty
    """
    Given a cell type, returns a list of Cell objects of the given type
    Options are: ['resource', 'researched resource', 'player citytile', 'enemy citytile', 'empty']
    """
    cells_of_type = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if (
                    ( cell_type == 'resource' and cell.has_resource() ) \
                or ( cell_type == 'researched resource' and cell.has_resource() and researched(cell.resource, player) ) \
                or ( cell_type == 'player citytile' and cell.citytile is not None and cell.citytile.team == observation.player ) \
                or ( cell_type == 'enemy citytile' and cell.citytile is not None and cell.citytile.team != observation.player ) \
                or ( cell_type == 'empty' and cell.citytile is None and not cell.has_resource() )
            ):
                cells_of_type.append(cell)
    
    return cells_of_type


def move_unit(unit, position, citytile_cells, actions):
    """
    moves the given unit towards the given position
    also checks basic collision detection, and adds annotations for any movement
    """

    direction = unit.pos.direction_to(position)
    target_tile = unit.pos.translate(direction, 1)
    
    # if target_tile is not being targeted already, move there
    if target_tile not in target_tiles or target_tile in [tile.pos for tile in citytile_cells]:
        target_tiles.append(target_tile)
        actions.append(unit.move(direction))
        actions.append(annotate.line(unit.pos.x, unit.pos.y, position.x, position.y))

    # else, mark an X on the map
    else:
        actions.append(annotate.x(target_tile.x, target_tile.y))


def go_home(unit, citytile_cells, actions):
    """
    moves the given unit towards the nearest citytile
    """

    nearest_citytile_position = find_nearest_position(unit.pos, citytile_cells)
    move_unit(unit, nearest_citytile_position, citytile_cells, actions)
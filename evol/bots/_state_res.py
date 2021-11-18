from lux.game_map import Position, Cell
import os, sys
from typing import List, Tuple, Union, Dict

if os.path.exists("/kaggle"):  # check if we're on a kaggle server
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)  # log to stdout on kaggle
    logger.addHandler(handler)
else:
    from loguru import logger  # log to file locally
from statements import TilesCollection, TileStatesCollection


class AdjacentToResourceTilesCollection:

    def __init__(
        self,
        tiles: TilesCollection,
        states: TileStatesCollection
        ) -> None:

        self.tiles = tiles
        self.game_state = tiles.game_state
        self.resources = tiles.resources
        self.states = states

        self.__empty_adjacent_any = None
        
        self.__empty_adjacent_one_any_res = None
        self.__empty_adjacent_two_any_res = None
        self.__empty_adjacent_three_any_res = None
        self.__empty_adjacent_any_pos = None
        self.__empty_adjacent_one_any_res_pos = None
        self.__empty_adjacent_two_any_res_pos = None
        self.__empty_adjacent_three_any_res_pos = None

        self.__empty_adjacent_one_wood_res = None
        self.__empty_adjacent_two_wood_res = None
        self.__empty_adjacent_three_wood_res = None
        self.__empty_adjacent_one_wood_res_pos = None
        self.__empty_adjacent_two_wood_res_pos = None
        self.__empty_adjacent_three_wood_res_pos = None

        self.__empty_adjacent_one_coal_res = None
        self.__empty_adjacent_two_coal_res = None
        self.__empty_adjacent_three_coal_res = None
        self.__empty_adjacent_one_coal_res_pos = None
        self.__empty_adjacent_two_coal_res_pos = None
        self.__empty_adjacent_three_coal_res_pos = None

        self.__empty_adjacent_one_uranium_res = None
        self.__empty_adjacent_two_uranium_res = None
        self.__empty_adjacent_three_uranium_res = None
        self.__empty_adjacent_one_uranium_res_pos = None
        self.__empty_adjacent_two_uranium_res_pos = None
        self.__empty_adjacent_three_uranium_res_pos = None

        self.__empty_adjacent_wood_coal_res = None
        self.__empty_adjacent_wood_coal_res_pos = None
        self.__empty_adjacent_coal_uranium_res = None
        self.__empty_adjacent_coal_uranium_res_pos = None
        self.__empty_adjacent_wood_coal_uranium_res = None
        self.__empty_adjacent_wood_coal_uranium_res_pos = None

    @property
    def empty_adjacent_any(self) -> Dict[int, Dict[Cell, List[str]]]:
        """
        Collects list of all empty cells, adjacent to any resource in form [(Cell, resource type)].
        Transforms this list in dictionary of cells and types of adjacent resources in form:
                {Cell: [resource type, resource type]}
        by combining repeating Cells.
        Finally split dictionary in parts according to number of adjacent resources and returns it.

        Args:
        Returns:
            Dict[N: Dict[Cell: List[resource types]]]
        """

        if self.__empty_adjacent_any is None:
            self.__empty_adjacent_any = {1: {}, 2: {}, 3: {}}
            adj_to_res_cells = []
            for cell in self.resources:
                adjacent_cells = self.states.get_state(pos=cell.pos).adjacent
                for adj_cell_pos in adjacent_cells:
                    cell_obj = self.game_state.map.get_cell_by_pos(adj_cell_pos)
                    if cell_obj.resource is None and cell_obj.citytile is None:  # and cell_obj.road == 0:  #TODO: decide if road level should be checked or we can build right on the road
                        adj_to_res_cells.append((cell_obj, cell.resource.type))
            adj_cells_dict = {}
            for cell, resource in adj_to_res_cells:
                adj_cells_dict.setdefault(cell, []).append(resource)

            for length in range(1, 4):
                for cell, res in adj_cells_dict.items():
                    if len(res) == length:
                        self.__empty_adjacent_any[length].setdefault(cell, res)

        return self.__empty_adjacent_any

    @property
    def empty_adjacent_one_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to one resource tiles of any type.

        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_one_any_res is None:
            self.__empty_adjacent_one_any_res = self.empty_adjacent_any[1]
        return self.__empty_adjacent_one_any_res

    @property
    def empty_adjacent_one_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_any_res_pos is None:
            self.__empty_adjacent_one_any_res_pos = [cell.pos for cell in self.empty_adjacent_one_any_res]
        return self.__empty_adjacent_one_any_res_pos

    @property
    def empty_adjacent_two_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to two resource tiles of any type.

        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_two_any_res is None:
            self.__empty_adjacent_two_any_res = self.empty_adjacent_any[2]
        return self.__empty_adjacent_two_any_res

    @property
    def empty_adjacent_two_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_any_res_pos is None:
            self.__empty_adjacent_two_any_res_pos = [cell.pos for cell in self.empty_adjacent_two_any_res]
        return self.__empty_adjacent_two_any_res_pos

    @property
    def empty_adjacent_three_any_res(self) -> Dict[Cell, str]:
        """
        Returns dict of Cells close to three resource tiles of any type.
        Args:
        Returns:
            Dict[Cell, [resource type]]: list of cells.
        """
        if self.__empty_adjacent_three_any_res is None:
            self.__empty_adjacent_three_any_res = self.empty_adjacent_any[3]
        return self.__empty_adjacent_three_any_res

    @property
    def empty_adjacent_three_any_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three resource tile of any type.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_any_res_pos is None:
            self.__empty_adjacent_three_any_res_pos = [cell.pos for cell in self.empty_adjacent_three_any_res]
        return self.__empty_adjacent_three_any_res_pos

    @property
    def empty_adjacent_one_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to one resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_one_wood_res is None:
            self.__empty_adjacent_one_wood_res = [cell for cell, resource in self.empty_adjacent_one_any_res.items()
                                                  if {'wood'} == set(resource)]
        return self.__empty_adjacent_one_wood_res

    @property
    def empty_adjacent_one_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_wood_res_pos is None:
            self.__empty_adjacent_one_wood_res_pos = [cell.pos for cell in self.empty_adjacent_one_wood_res]
        return self.__empty_adjacent_one_wood_res_pos

    @property
    def empty_adjacent_two_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to two resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_two_wood_res is None:
            self.__empty_adjacent_two_wood_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                  if {'wood'} == set(resource)]
        return self.__empty_adjacent_two_wood_res

    @property
    def empty_adjacent_two_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_wood_res_pos is None:
            self.__empty_adjacent_two_wood_res_pos = [cell.pos for cell in self.empty_adjacent_two_wood_res]
        return self.__empty_adjacent_two_wood_res_pos

    @property
    def empty_adjacent_three_wood_res(self) -> List[Cell]:
        """
        Returns list of Cells close to three resource tiles with wood.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_three_wood_res is None:
            self.__empty_adjacent_three_wood_res = [cell for cell, resource in self.empty_adjacent_three_any_res.items()
                                                    if {'wood'} == set(resource)]
        return self.__empty_adjacent_three_wood_res

    @property
    def empty_adjacent_three_wood_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three wood resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_wood_res_pos is None:
            self.__empty_adjacent_three_wood_res_pos = [cell.pos for cell in self.empty_adjacent_three_wood_res]
        return self.__empty_adjacent_three_wood_res_pos

    @property
    def empty_adjacent_one_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to one resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_one_coal_res is None:
            self.__empty_adjacent_one_coal_res = [cell for cell, resource in self.empty_adjacent_one_any_res.items()
                                                  if {'coal'} == set(resource)]
        return self.__empty_adjacent_one_coal_res

    @property
    def empty_adjacent_one_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_coal_res_pos is None:
            self.__empty_adjacent_one_coal_res_pos = [cell.pos for cell in self.empty_adjacent_one_coal_res]
        return self.__empty_adjacent_one_coal_res_pos

    @property
    def empty_adjacent_two_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to two resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_two_coal_res is None:
            self.__empty_adjacent_two_coal_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                  if {'coal'} == set(resource)]
        return self.__empty_adjacent_two_coal_res

    @property
    def empty_adjacent_two_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_coal_res_pos is None:
            self.__empty_adjacent_two_coal_res_pos = [cell.pos for cell in self.empty_adjacent_two_coal_res]
        return self.__empty_adjacent_two_coal_res_pos

    @property
    def empty_adjacent_three_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to three resource tiles with coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_three_coal_res is None:
            self.__empty_adjacent_three_coal_res = [cell for cell, resource in self.empty_adjacent_three_any_res.items()
                                                    if {'coal'} == set(resource)]
        return self.__empty_adjacent_three_coal_res

    @property
    def empty_adjacent_three_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_coal_res_pos is None:
            self.__empty_adjacent_three_coal_res_pos = [cell.pos for cell in self.empty_adjacent_three_coal_res]
        return self.__empty_adjacent_three_coal_res_pos

    @property
    def empty_adjacent_one_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to one resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_one_uranium_res is None:
            self.__empty_adjacent_one_uranium_res = [cell for cell, resource in self.empty_adjacent_one_any_res.items()
                                                     if {'uranium'} == set(resource)]
        return self.__empty_adjacent_one_uranium_res

    @property
    def empty_adjacent_one_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to one uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_one_uranium_res_pos is None:
            self.__empty_adjacent_one_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_one_uranium_res]
        return self.__empty_adjacent_one_uranium_res_pos

    @property
    def empty_adjacent_two_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to two resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_two_uranium_res is None:
            self.__empty_adjacent_two_uranium_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                     if {'uranium'} == set(resource)]
        return self.__empty_adjacent_two_uranium_res

    @property
    def empty_adjacent_two_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to two uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_two_uranium_res_pos is None:
            self.__empty_adjacent_two_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_two_uranium_res]
        return self.__empty_adjacent_two_uranium_res_pos

    @property
    def empty_adjacent_three_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to three resource tiles with uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_three_uranium_res is None:
            self.__empty_adjacent_three_uranium_res = [cell for cell, resource in
                                                       self.empty_adjacent_three_any_res.items()
                                                       if {'uranium'} == set(resource)]
        return self.__empty_adjacent_three_uranium_res

    @property
    def empty_adjacent_three_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to three uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_three_uranium_res_pos is None:
            self.__empty_adjacent_three_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_three_uranium_res]
        return self.__empty_adjacent_three_uranium_res_pos

    @property
    def empty_adjacent_wood_coal_res(self) -> List[Cell]:
        """
        Returns list of Cells close to both types of resource: wood and coal.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_wood_coal_res is None:
            self.__empty_adjacent_wood_coal_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                   if {'wood', 'coal'} == set(resource)] + \
                                                  [cell for cell, resource in self.empty_adjacent_three_any_res.items()
                                                   if {'wood', 'coal'} == set(resource)]
        return self.__empty_adjacent_wood_coal_res

    @property
    def empty_adjacent_wood_coal_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to wood and coal resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_wood_coal_res_pos is None:
            self.__empty_adjacent_wood_coal_res_pos = [cell.pos for cell in self.empty_adjacent_wood_coal_res]
        return self.__empty_adjacent_wood_coal_res_pos

    @property
    def empty_adjacent_coal_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to both types of resource: coal and uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_coal_uranium_res is None:
            self.__empty_adjacent_coal_uranium_res = [cell for cell, resource in self.empty_adjacent_two_any_res.items()
                                                      if {'coal', 'uranium'} == set(resource)] + \
                                                     [cell for cell, resource in
                                                      self.empty_adjacent_three_any_res.items()
                                                      if {'coal', 'uranium'} == set(resource)]

        return self.__empty_adjacent_coal_uranium_res

    @property
    def empty_adjacent_coal_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to coal and uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_coal_uranium_res_pos is None:
            self.__empty_adjacent_coal_uranium_res_pos = [cell.pos for cell in self.empty_adjacent_coal_uranium_res]
        return self.__empty_adjacent_coal_uranium_res_pos

    @property
    def empty_adjacent_wood_coal_uranium_res(self) -> List[Cell]:
        """
        Returns list of Cells close to both types of resource: coal and uranium.

        Args:
        Returns:
            List[Cell]: list of cells.
        """
        if self.__empty_adjacent_wood_coal_uranium_res is None:
            self.__empty_adjacent_wood_coal_uranium_res = [cell for cell, resource
                                                           in self.empty_adjacent_three_any_res.items()
                                                           if {'wood', 'coal', 'uranium'} == set(resource)]

        return self.__empty_adjacent_wood_coal_uranium_res

    @property
    def empty_adjacent_wood_coal_uranium_res_pos(self) -> List[Position]:
        """
        Returns list of positions of Cells close to wood, coal and uranium resource tile.

        Args:
        Returns:
            List[Position]: game_map.Position object for coordinate of Cell (x: int, y: int).
        """
        if self.__empty_adjacent_wood_coal_uranium_res_pos is None:
            self.__empty_adjacent_wood_coal_uranium_res_pos = [cell.pos for cell
                                                               in self.empty_adjacent_wood_coal_uranium_res]
        return self.__empty_adjacent_wood_coal_uranium_res_pos
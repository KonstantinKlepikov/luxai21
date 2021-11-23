from lux.game_map import Cell
import os, sys
from typing import Set

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
        self.states = states

        self.__empty_adjaced_wood = None
        self.__empty_adjaced_coal = None
        self.__empty_adjaced_uranium = None
        self.__empty_adjaced_wood_and_coal = None
        self.__empty_adjaced_wood_and_uranium = None
        self.__empty_adjaced_coal_and_uranium = None
        self.__empty_adjaced_any = None

    @property
    def empty_adjaced_wood(self) -> Set[Cell]:
        """
        Collects set of all empty adjaced to wood cells

        Returns:
            Set[Cell]
        """
        if self.__empty_adjaced_wood is None:
            adj_to = set()
            for pos in self.tiles.woods_pos:
                state = self.states.get_state(pos=pos)
                for adj_pos in state.adjaced:
                    adj_state = self.states.get_state(pos=adj_pos)
                    if adj_state.is_empty:
                        cell = self.tiles.game_state.map.get_cell_by_pos(adj_pos)
                        adj_to.add((cell))
            self.__empty_adjaced_wood = adj_to
        return self.__empty_adjaced_wood
    
    @property
    def empty_adjaced_coal(self) -> Set[Cell]:
        """
        Collects set of all empty adjaced to coal cells

        Returns:
            Set[Cell]
        """
        if self.__empty_adjaced_coal is None:
            adj_to = set()
            for pos in self.tiles.coals_pos:
                state = self.states.get_state(pos=pos)
                for adj_pos in state.adjaced:
                    adj_state = self.states.get_state(pos=adj_pos)
                    if adj_state.is_empty:
                        cell = self.tiles.game_state.map.get_cell_by_pos(adj_pos)
                        adj_to.add((cell))
            self.__empty_adjaced_coal = adj_to
        return self.__empty_adjaced_coal
    
    @property
    def empty_adjaced_uranium(self) -> Set[Cell]:
        """
        Collects set of all empty adjaced to uranium cells

        Returns:
            Set[Cell]
        """
        if self.__empty_adjaced_uranium is None:
            adj_to = set()
            for pos in self.tiles.uraniums_pos:
                state = self.states.get_state(pos=pos)
                for adj_pos in state.adjaced:
                    adj_state = self.states.get_state(pos=adj_pos)
                    if adj_state.is_empty:
                        cell = self.tiles.game_state.map.get_cell_by_pos(adj_pos)
                        adj_to.add((cell))
            self.__empty_adjaced_uranium = adj_to
        return self.__empty_adjaced_uranium

    @property
    def empty_adjaced_wood_and_coal(self) -> Set[Cell]:
        """
        Collects set of all empty cells, adjaced to wood and coal
        
        Returns:
            Set[Cell]
        """
        if self.__empty_adjaced_wood_and_coal is None:
            self.__empty_adjaced_wood_and_coal = set().union(
                    self.empty_adjaced_wood,
                    self.empty_adjaced_coal
                    )
        return self.__empty_adjaced_wood_and_coal
    
    @property
    def empty_adjaced_coal_and_uranium(self) -> Set[Cell]:
        """
        Collects set of all empty cells, adjaced to coal and uranium
        
        Returns:
           Set[Cell]
        """
        if self.__empty_adjaced_coal_and_uranium is None:
            self.__empty_adjaced_coal_and_uranium = set().union(
                self.empty_adjaced_coal,
                self.empty_adjaced_uranium
                )
        return self.__empty_adjaced_coal_and_uranium
    
    @property
    def empty_adjaced_wood_and_uranium(self) -> Set[Cell]:
        """
        Collects set of all empty cells, adjaced to wood and uranium
        
        Returns:
            Set[Cell]
        """
        if self.__empty_adjaced_wood_and_uranium is None:
            self.__empty_adjaced_wood_and_uranium = set().union(
                self.empty_adjaced_wood,
                self.empty_adjaced_uranium
                )
        return self.__empty_adjaced_wood_and_uranium

    @property
    def empty_adjaced_any(self) -> Set[Cell]:
        """
        Collects set of all empty cells, adjaced to any resource
        
        Returns:
            Set[Cell]
        """
        if self.__empty_adjaced_any is None:
            self.__empty_adjaced_any = set().union(
                self.empty_adjaced_wood,
                self.empty_adjaced_coal,
                self.empty_adjaced_uranium
                )
        return self.__empty_adjaced_any
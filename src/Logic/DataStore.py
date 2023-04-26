import json

from typing import List

from .Entities.organism import Organism
from .Entities.vegetation import Vegetation


class DataStore(object):
    """This class contains the data logic of a simulation.
    """
    def __init__(self, s_path: str):
        self.session_path: str = s_path
        self.organisms: List[Organism] = []
        self.vegetation: List[Vegetation] = []
        self.foodChain: dict = {}

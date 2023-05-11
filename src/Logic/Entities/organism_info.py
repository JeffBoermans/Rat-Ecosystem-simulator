from typing import Tuple


class OrganismInfo:
    """Properties specific to a species, to be shared between
    Organism instances.
    """
    def __init__(self, o_m: int, o_b: int, o_ls: Tuple[int, int], o_mpa: int):
        """
        :param o_m: Sexual maturity (days)
        :param o_b: Breeding age (days)
        :param o_ls: Life span, represented as a tuple (months)
        :param o_mpa: Start menopause (days)
        """
        self.maturity: int = o_m
        self.breeding: int = o_b
        self.lifespan = o_ls
        self.menopause = o_mpa
class OrganismInfo:
    """Properties specific to a species, to be shared between
    Organism instances.
    """
    def __init__(self, o_m: int, o_b: int, o_ls: list[int], o_mpa: list[int]):
        """
        :param o_m: Sexual maturity (days)
        :param o_b: Breeding age (days)
        :param o_ls: Life span, represented in a list (months)
        :param o_mpa: Start menopause (months)
        :return:

        lifespan: in days
        """
        self.maturity: int = o_m
        self.breeding: int = o_b
        self._month_to_days(o_ls)
        self.lifespan = o_ls
        self._month_to_days(o_mpa)
        self.menopause = o_mpa

    def _month_to_days(self, o: list[int]):
        for i in range(0,len(o)):
            o[i] *= 30
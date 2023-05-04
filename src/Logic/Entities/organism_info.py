class OrganismInfo:
    def __init__(self, o_m: int, o_b: int, o_ls, o_mpa: int):
        """
        :param o_m: Sexual maturity (days)
        :param o_b: Breeding age (days)
        :param o_ls: Life span, represented in a list (months)
        :param o_mpa: Start menopause (days)
        :return:
        """
        self.maturity: int = o_m
        self.breeding: int = o_b
        self.lifespan = o_ls
        self.menopause = o_mpa
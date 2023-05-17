from typing import Tuple
from statistics import NormalDist


def centered_normal_dist(range: Tuple[int, int], std_factor: float=4.0) -> NormalDist:
    """Create a normal distribution centered on the middle of the specified range.
    
    Suppose the width of the range is named x, then the standard deviation of the
    resulting normal distribution is calculated as:
        x / std_factor
    
    :param range: The range to center a normal dist on
    :param std_factor: The inverse scaling factor on the the range width to produce the std
    :return: The centered normal distribution
    """
    range_dist: int = range[1] - range[0]
    range_std: int = range_dist / std_factor
    mean: int = range[0] + range_std
    return NormalDist(mu=mean, sigma=range_std)

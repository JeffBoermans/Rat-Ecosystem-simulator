from typing import Tuple
from statistics import NormalDist
from datetime import datetime


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



class Logger():
    def __init__(self, file_path: str) -> None:
        self.file = file_path

    def log(self, msg: str) -> None:
        """ Logs the message with the current date and time
        """
        file = open(self.file, 'a')
        file.write(f"[{datetime.now()}] : {msg}\n")
        file.close()
    
    def setup(self, input_file: str) -> None:
        """ Sets up file with custom beautiful '='-art. 
        """
        file = open(self.file, 'w')
        file.write("==================================================================\n")
        file.write(f"Log created on: {datetime.now()}\n")
        file.write(f"Input file used: {input_file}\n")
        file.write("IMPORTANT: Save this file externally, starting a new simulation will clear this file\n")
        file.write("==================================================================\n")
        file.close()

    def logNoTimestamp(self, msg: str) -> None:
        """ Prints the message without timestamp
        """
        file = open(self.file, 'a')
        file.write(f"{msg}\n")
        file.close()

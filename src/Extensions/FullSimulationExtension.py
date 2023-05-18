from ..Logic.Extensions.SimulationExtension import SimulationExtension
from ..UI.Extensions.SimulationExtensionUI import SimulationExtensionUI


class FullSimulationExtension(SimulationExtension, SimulationExtensionUI):
    """A metaclass to resolve meta class conflicts resulting from combining logic and ui extensions."""

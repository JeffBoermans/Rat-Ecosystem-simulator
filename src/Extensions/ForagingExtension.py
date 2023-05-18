from ..Logic.Extensions.ForagingExtension import ForagingExtension
from ..UI.Extensions.ForagingExtensionUI import ForagingExtensionUI
from .FullSimulationExtension import FullSimulationExtension

class ForagingExtensionFull(ForagingExtension, ForagingExtensionUI):
    """A combination of the UIful and logical foraging extensions."""
    __metaclass__ = FullSimulationExtension

    def __init__(self, extension_name: str = 'foraging') -> None:
        super(ForagingExtensionFull, self).__init__(extension_name)
        ForagingExtensionUI.__init__(self)

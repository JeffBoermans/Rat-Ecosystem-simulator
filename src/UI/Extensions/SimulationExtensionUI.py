class SimulationExtensionUI(object):
    """The UI interface of a simulation extension"""
    def add_ui_elements(self, ui) -> None:
        """Single time use, add UI elements to the dearpy ui of the UI instance."""
        pass

    def update_ui_elements(self, ui) -> None:
        """Update the ui elements added by this extention through its ui addition method."""
        pass
